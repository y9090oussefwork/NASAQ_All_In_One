import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import check_selection as selection
import check_web_catalog as web

REG = selection.load_json(ROOT / 'assets/providers.json')
CAP = selection.load_json(ROOT / 'assets/capabilities.json')
MAP = selection.load_json(ROOT / 'assets/web-source-map.json')
COVERAGE = selection.load_json(ROOT / 'assets/web-coverage.json')


class WebCatalogTests(unittest.TestCase):
    def setUp(self):
        self.registry = copy.deepcopy(REG)
        self.source_map = copy.deepcopy(MAP)
        self.coverage = copy.deepcopy(COVERAGE)

    def codes(self):
        return {i['code'] for i in web.validate_web_catalog(self.source_map, self.coverage, self.registry, CAP)}

    def source(self, research_id):
        return next(s for s in self.source_map['sources'] if s['research_id'] == research_id)

    def test_prepared_data_is_consistent_without_activation(self):
        self.assertEqual(set(), self.codes())

    def test_research_cannot_be_used_as_runtime_registry(self):
        plan = selection.load_json(ROOT / 'assets/examples/web-selection.draft.json')
        research = {'schema_version': '1.0-research', 'sources': self.source_map['sources']}
        self.assertIn('invalid_registry', {i['code'] for i in selection.validate_selection(plan, research, CAP)})

    def test_no_original_provider_was_removed(self):
        self.registry['providers'] = [p for p in self.registry['providers'] if p['id'] != 'mysql-docs']
        self.assertIn('web_unknown_provider', self.codes())

    def test_role_alias_cannot_bypass_selection_guard(self):
        plan = selection.load_json(ROOT / 'assets/examples/web-selection.draft.json')
        for kind in ['executor', 'skill-library', 'unknown-kind', []]:
            with self.subTest(kind=kind):
                reg = copy.deepcopy(REG)
                next(p for p in reg['providers'] if p['id'] == 'playwright-cli')['kind'] = kind
                self.assertIn('invalid_registry', {i['code'] for i in selection.validate_selection(plan, reg, CAP)})

    def test_source_cannot_declare_unknown_capability(self):
        self.registry['providers'][0]['capabilities'].append('unknown.capability')
        self.assertIn('web_invalid_provider', self.codes())

    def test_reference_cannot_own_execution(self):
        plan = selection.load_json(ROOT / 'assets/examples/web-selection.draft.json')
        binding = next(b for b in plan['bindings'] if b['id'] == 'api-contract')
        binding.update(provider='openapi', activation_mode='versioned-reference')
        self.assertIn('reference_role', {i['code'] for i in selection.validate_selection(plan, REG, CAP)})

    def test_grouped_tools_cannot_be_promoted_to_owners(self):
        self.source('T02')['targets'][0]['role'] = 'primary'
        self.assertIn('web_invalid_role', self.codes())

    def test_visual_reviewer_remains_reviewer(self):
        self.source('S35')['targets'][0]['role'] = 'primary'
        self.assertIn('web_invalid_role', self.codes())

    def test_grouped_identity_and_authorization_are_separate(self):
        roles = {t['provider_id']: t['responsibility'] for t in self.source('R18')['targets']}
        self.assertEqual({'keycloak-docs': 'identity', 'openfga-docs': 'authorization'}, roles)
        self.source('R18')['targets'][1]['provider_id'] = 'keycloak-docs'
        self.assertIn('web_unknown_provider', self.codes())

    def test_missing_or_duplicate_mapping_id_is_rejected(self):
        self.source_map['sources'].append(copy.deepcopy(self.source_map['sources'][0]))
        self.assertIn('web_invalid_id', self.codes())

    def test_non_namespaced_coverage_is_rejected(self):
        self.coverage['rows'][0]['id'] = 'w01-01'
        self.assertIn('web_invalid_id', self.codes())

    def test_unknown_source_reference_is_rejected(self):
        self.coverage['rows'][0]['proposed_source_refs'] = ['web.missing']
        self.assertIn('web_unknown_source', self.codes())

    def test_unknown_capability_reference_is_rejected(self):
        self.coverage['rows'][0]['capability_ids'] = ['missing.capability']
        self.assertIn('web_unknown_capability', self.codes())

    def test_gap_cannot_reference_nonexistent_coverage(self):
        self.coverage['gaps'][0]['topics'] = ['web.w99-99']
        self.assertIn('web_unknown_source', self.codes())

    def test_proposed_evaluation_cannot_claim_a_run(self):
        self.coverage['evaluations'][0]['status'] = 'passed'
        self.assertIn('web_activation_forbidden', self.codes())

    def test_research_cannot_enable_installation(self):
        self.source_map['automatic_activation_allowed'] = True
        self.assertIn('web_activation_forbidden', self.codes())

    def test_unverified_source_cannot_be_marked_tested(self):
        self.source('S02')['runtime_tested'] = True
        self.assertIn('web_activation_forbidden', self.codes())

    def test_malformed_applicability_and_relation_return_errors(self):
        self.coverage['rows'][0]['applicability'] = []
        self.source_map['sources'][0]['relation'] = []
        self.assertTrue({'web_invalid_scope', 'web_invalid_relation'} <= self.codes())

    def test_complementary_api_tools_can_coexist(self):
        plan = {'schema_version': 1, 'components': {'api': {'tags': ['api', 'openapi']}},
                'required_slots': [], 'activation_conflicts': [], 'bindings': []}
        for pid in ['spectral', 'schemathesis']:
            plan['bindings'].append({'id': pid, 'provider': pid, 'capability': 'api.contract',
              'component': 'api', 'phase': 'verification', 'role': 'executor',
              'writes': ['evidence/' + pid], 'scope_contract': 'Separate static/runtime checks',
              'activation_mode': 'reviewed-cli'})
        self.assertEqual([], selection.validate_selection(plan, REG, CAP))
        incompatible = copy.deepcopy(plan)
        incompatible['components']['api']['tags'] = ['api']
        self.assertEqual(2, sum(i['code'] == 'stack_mismatch'
                               for i in selection.validate_selection(incompatible, REG, CAP)))
        row = next(r for r in self.coverage['rows'] if r['research_id'] == 'W09-03')
        self.assertEqual('complements', row['source_relation'])

    def test_data_transform_and_storage_have_distinct_responsibilities(self):
        warehouse = next(p for p in REG['providers'] if p['id'] == 'clickhouse')
        transform = next(p for p in REG['providers'] if p['id'] == 'dbt')
        self.assertFalse(set(warehouse['capabilities']) & set(transform['capabilities']))
        for rid in ['W11-18', 'W06-10']:
            row = next(r for r in self.coverage['rows'] if r['research_id'] == rid)
            self.assertEqual('complements', row['source_relation'])

    def test_web_documentation_candidates_remain_references(self):
        providers = {p['id']: p for p in REG['providers']}
        for cap in CAP['capabilities']:
            if cap['id'] in {'backend.python', 'backend.node', 'data.local-relational'}:
                self.assertTrue(cap['primary_candidates'])
                for pid in cap['primary_candidates']:
                    self.assertNotIn(providers[pid]['kind'], {'official-reference', 'standard'})
                self.assertTrue(any(providers[pid]['kind'] == 'official-reference'
                                    for pid in cap['complements']))

    def test_shared_contract_keeps_distinct_requirement_ids(self):
        rows = [r for r in self.coverage['rows'] if r['research_id'] in {'W03-04', 'W11-04'}]
        self.assertEqual(2, len({r['id'] for r in rows}))
        self.assertEqual({'seller-dashboard'}, {r['shared_contract_id'] for r in rows})

    def test_supplied_research_snapshot_when_workspace_available(self):
        source = ROOT.parents[1] / MAP['research_provenance']['path']
        if not source.exists():
            self.skipTest('Original research is intentionally not bundled in standalone skill')
        self.assertEqual(MAP['research_provenance']['sha256'], hashlib.sha256(source.read_bytes()).hexdigest())
        research = selection.load_json(source)
        self.assertEqual({r['id'] for r in research['sources']}, {r['research_id'] for r in MAP['sources']})
        self.assertEqual({r['id'] for r in research['coverage']}, {r['research_id'] for r in COVERAGE['rows']})

    def test_cli_locales_invalid_input_and_no_writes(self):
        files = [ROOT / 'assets' / name for name in ['providers.json','capabilities.json','web-source-map.json','web-coverage.json']]
        before = {str(p): p.read_bytes() for p in files}
        for lang in ['ar', 'en']:
            run = subprocess.run([sys.executable, '-B', str(ROOT/'scripts/check_web_catalog.py'), '--lang', lang, '--json'],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(0, run.returncode, run.stderr)
            self.assertFalse(json.loads(run.stdout)['integrations_executed'])
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp)/'bad.json'
            bad.write_text('{"schema_version":1,"schema_version":2}', encoding='utf-8')
            run = subprocess.run([sys.executable, '-B', str(ROOT/'scripts/check_web_catalog.py'), '--map', str(bad), '--json'],
                                 capture_output=True, text=True, check=False)
            self.assertEqual(2, run.returncode)
            self.assertEqual('input_error', json.loads(run.stdout)['status'])
        self.assertEqual(before, {str(p): p.read_bytes() for p in files})


if __name__ == '__main__':
    unittest.main()
