# Calibration configs -> R6 provenance map (2026-08-15)
# calib_sha256 = content_hash(canonical_json(config)) [nsclinfs.hashing.content_hash], NOT the file byte-sha.
# Verify with: python -c "import json,sys;sys.path.insert(0,'src');from nsclinfs.hashing import content_hash;print(content_hash(json.load(open('<file>'))))"

calibration_highdim_arrhythmia.json
  content_hash (R6 stamp) = 6cbf6ff6a5edcd154591f80e129fa228adb6fbf2f599d3a819231082884e93dd
  file_sha256 (transport)  = 9e324223217f0ed501b11c5cc4a5de35569d2bd4d3ae80593f6285bbf02e0514
  produced: summary_arrhythmia.csv

calibration_tier7_n100.json
  content_hash (R6 stamp) = aa4b87ddd7e9344f1e6a2d2fd790dca11aac9977072c5be628da516f5562fa90
  file_sha256 (transport)  = c7d4c792ce52e0daa94c67a5750c055ff57200be47375b1a3a1d90942ca38e33
  produced: summary_arrhythmia_n100.csv

calibration_tier7_n150.json
  content_hash (R6 stamp) = 010091f799c130c0a067ab482bbdca1153e25a4f73dc5d374089b7a82572ad6d
  file_sha256 (transport)  = d3920d8eee56808bd32566926287e02226b83026bbe44ed1bbc243848adfc126
  produced: summary_arrhythmia_n150.csv

calibration_tier7_n250.json
  content_hash (R6 stamp) = 129316fe2217a89eed91ec028d0bd18536910f999b82edc8d6654755b2bea9b7
  file_sha256 (transport)  = 90f6b4831702de3d9fb5ee66c0276cf65d8183fdf99036f79f3dc2f5d971f6c1
  produced: summary_arrhythmia_n250.csv

calibration_highdim.json
  content_hash (R6 stamp) = eea1cc34fd9d82b0c6d7267dcc1cac30b2234f9f9020f48754a66d120f25f54e
  file_sha256 (transport)  = 489a813b60c9f19ce32e34d01feebb8287f4940178acac0fbb83ea43c74af057
  produced: summary_arcene.csv / summary_gli85.csv / summary_prostate_ge.csv

calibration_tier3.json
  content_hash (R6 stamp) = e23d49d8a7ff8deab9921d270751b0776348543fbb206713fdfdfabd6402c8af
  file_sha256 (transport)  = a71d37cd34b4b0e147ca3ec457a7c9d0056b013190e8bd42ffb9b4e85807fd9d
  produced: summary_tier3_11ds.csv / summary_tier3_d130.csv
