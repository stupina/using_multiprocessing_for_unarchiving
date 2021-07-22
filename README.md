# Using multiprocessing for unarchiving
Test 3 multiprocessing approaches for files unarchiving:
 * Pool map
 * Simple queue
 * Ordered queue

## Scripts:
 * archive_files - uses to prepare files for testing
 * test_multiprocessing - uses to test approaches

## Results:
|Name        |Archived data size|Proceses amount|Data description                                                      |Execution time 1  |Execution time 2  |Average time     |
|------------|------------------|---------------|----------------------------------------------------------------------|------------------|------------------|-----------------|
|Pool Map    |20,6 ГБ           |3              |Couple data pieces are about 6-7gb, couple ~ 800mb, other are ~ 100kb |834.6287879943848 |800.6480705738068 |817.638429284096 |
|Simple Queue|20,6 ГБ           |3              |Couple data pieces are about 6-7gb, couple ~ 800mb, other are ~ 100kb |770.4904053211212 |795.0200545787811 |782.755229949951 |
|Ranged Queue|20,6 ГБ           |3              |Couple data pieces are about 6-7gb, couple ~ 800mb, other are ~ 100kb |755.7135365009308 |762.2702052593231 |758.991870880127 |
|Pool Map    |2,3 ГБ            |5              |A lot of files ~ 100kb                                                |1517.1853456497192|1455.369168996811 |1486.277257323265|
|Ranged Queue|2,3 ГБ            |5              |A lot of files ~ 100kb                                                |1365.1120266914368|1365.463413476944 |1365.287720084191|
|Simple Queue|2,3 ГБ            |5              |A lot of files ~ 100kb                                                |1404.375957250595 |1401.7894253730774|1403.082691311836|

As a result, for this purpose it is more efficient to use the Ranged Queue.
