import importlib.util, tempfile, pathlib, json, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('tide_update',(ROOT/'scripts/update_tides.py'))
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class TideRecovery(unittest.TestCase):
 def test_recovers_empty_station_manifest(self):
  with tempfile.TemporaryDirectory() as td:
   oldroot,oldjson,oldpred=mod.ROOT,mod.get_json,mod.get_predictions
   try:
    mod.ROOT=pathlib.Path(td)
    (mod.ROOT/'stations.json').write_text(json.dumps({'source':'NOAA CO-OPS','generated_at':None,'stations':[]}))
    mod.get_json=lambda url,timeout=25:{'stations':[]}
    def pred(st,begin,end,interval):
     if interval=='hilo':return [{'t':'2026-10-23 10:00','v':'9.5','type':'H'}]
     return [{'t':'2026-10-23 08:00','v':'7.0'}, {'t':'2026-10-23 08:06','v':'7.1'}]
    mod.get_predictions=pred
    mod.main()
    stations=json.loads((mod.ROOT/'stations.json').read_text())
    self.assertGreaterEqual(len(stations['stations']),1)
    self.assertEqual(stations['stations'][0]['id'],'9446484')
    self.assertEqual(json.loads((mod.ROOT/'tides/9446484.json').read_text())['source'],'NOAA CO-OPS')
   finally:
    mod.ROOT,mod.get_json,mod.get_predictions=oldroot,oldjson,oldpred
