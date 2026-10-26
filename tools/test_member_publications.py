"""Regression checks for automatic member selections; no external services."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from lxml import html
from member_publications import read_bibliography, is_member_first_author, add_alumni_publications


class MemberSyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'publications/2027').mkdir(parents=True)
        (self.root/'publications/2027/index.html').write_text('''<html><body>
        <p>(127) <a href="https://doi.org/10.1000/example">Synthetic member sync article</a></p>
        <p>C Zhang¹, J Wan¹, M Han*, X Lin</p>
        <p><em>Example Journal</em> 2027, 1, 100.</p></body></html>''')
        self.papers = read_bibliography(self.root)
        self.roster = {'evidence': {'127': {'doi': '10.1000/example',
            'full_authors': ['Chong Zhang', 'Ji Wan', 'Mengdi Han', 'Xiang Lin']}},
            'confirmed_author_positions': {}, 'excluded_representative_paper_ids': {}}

    def test_first_cofirst_and_middle_author(self):
        self.assertTrue(is_member_first_author('Chong Zhang',127,self.papers,self.roster))
        self.assertTrue(is_member_first_author('Ji Wan',127,self.papers,self.roster))
        self.assertFalse(is_member_first_author('Xiang Lin',127,self.papers,self.roster))
        self.assertFalse(is_member_first_author('Chi Zhang',127,self.papers,self.roster))

    def test_missing_identity_pi_and_exclusions(self):
        self.assertFalse(is_member_first_author('Chong Zhang',127,self.papers,{}))
        missing_pi = copy.deepcopy(self.papers)
        missing_pi[127]['authors'].remove('M Han*')
        self.assertFalse(is_member_first_author('Ji Wan',127,missing_pi,self.roster))
        self.roster['excluded_representative_paper_ids']['127'] = 'Excluded editorial'
        self.assertFalse(is_member_first_author('Ji Wan',127,self.papers,self.roster))

    def test_author_marker_changes(self):
        self.papers[127]['authors'][1] = 'J Wan'
        self.assertFalse(is_member_first_author('Ji Wan',127,self.papers,self.roster))
        self.roster['evidence']['127']['doi'] = '10.1000/different-paper'
        self.assertFalse(is_member_first_author('Chong Zhang',127,self.papers,self.roster))

    def test_alumni_addition_empty_state_and_duplicate_prevention(self):
        tree = html.document_fromstring('''<html><body><article class="alumni-member" data-member="Ji Wan">
        <div><button class="alumni-publications-toggle">Selected Publications</button></div>
        <div class="alumni-publications"><p class="alumni-paper-meta">-</p></div>
        </article></body></html>''')
        self.assertEqual(add_alumni_publications(tree,self.papers,self.roster),[{'member':'Ji Wan','paper_id':127}])
        self.assertEqual(add_alumni_publications(tree,self.papers,self.roster),[])
        panel = tree.xpath('//div[@class="alumni-publications"]')[0]
        self.assertEqual(len(panel.xpath('./p[@class="alumni-paper-title"]')),1)
        self.assertIn('Example Journal',panel.text_content())
        self.assertNotIn('> - <',html.tostring(panel,encoding='unicode'))
        self.assertEqual(tree.xpath('//button')[0].text,'Selected Publications (1)')

    def test_current_generator_ignores_stale_manual_id_list(self):
        (self.root/'data').mkdir(); (self.root/'current').mkdir()
        (self.root/'current/index.html').write_text('<html><body><header class="lab-header">Lab</header></body></html>')
        roster = dict(self.roster, groups=[['postdocs','Postdocs','博士后',[
            ['Chong Zhang','张翀','University / 大学']]]],member_roles={'Chong Zhang':'Postdoc'},
            member_paper_ids={'Chong Zhang':[]})
        (self.root/'data/member-publications.json').write_text(json.dumps(roster))
        (self.root/'data/group-photos.json').write_text('[]')
        script = Path(__file__).with_name('build_member_preview.py')
        subprocess.run([sys.executable,str(script),str(self.root),'--publish'],check=True,capture_output=True)
        page = html.document_fromstring((self.root/'current/index.html').read_text())
        self.assertEqual(page.xpath('//li/@data-paper-id'),['127'])


if __name__ == '__main__':
    unittest.main()
