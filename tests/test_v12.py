from pathlib import Path
import unittest,re,datetime
ROOT=Path(__file__).resolve().parents[1]
class V12Checks(unittest.TestCase):
 def test_tide_priority_and_date_controls(self):
  html=(ROOT/'docs/index.html').read_text();sidebar=html.split('<aside class="sidebar">')[1]
  assert sidebar.find('NOAA Tides')<sidebar.find('Surface current')<sidebar.find('DPV route planning')
  for id in ('tideDate','tideNextDay','tidePrevDay','nextTideEvents'):
   self.assertIn(f'id="{id}"',html)
 def test_flow_and_arrow_reactivity(self):
  js=(ROOT/'docs/dive-current.js').read_text()
  for token in ('function arrowGlyph(','function drawArrowMap()','visualizationSpeed=1300','stopFlowAnimation(); currentField=null','const currentFrameCache=new Map()','MAX_FRAME_CACHE=5'):
   self.assertIn(token,js)
  self.assertIn('const spacing=38',js)
 def test_forecast_and_tide_horizons(self):
  ss=(ROOT/'scripts/update_sscofs.py').read_text();t=(ROOT/'scripts/update_tides.py').read_text()
  self.assertIn('STRIDE = 2',ss)
  self.assertIn('60,66,72)',ss)
  self.assertIn('timedelta(days=14)',t)
 def test_null_tide_cache_does_not_crash(self):
  t=(ROOT/'scripts/update_tides.py').read_text()
  self.assertIn('AttributeError',t)
  self.assertIn("'id':'9446484'",t)
 def test_validity_and_no_fake_values(self):
  js=(ROOT/'docs/dive-current.js').read_text()
  for phrase in ('Selected time is outside verified NOAA forecast coverage','No verified forecast published yet','No cached tide predictions'):
   self.assertIn(phrase,js)
  self.assertNotIn('syntheticTide',js)
if __name__=='__main__':unittest.main()
