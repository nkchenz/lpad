#coding: utf8

import json
import urllib2
import urllib


def showsome(artist, title):
  query = urllib.urlencode({'q': ' '.join([title, artist, 'filetype:lrc'])})
  #query = urllib.urlencode({'q': searchfor})
  url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
  search_response = urllib2.urlopen(url)
  search_results = search_response.read().decode("utf8")
  results = json.loads(search_results)
  data = results['responseData']
  print results
  print('Total results: %s' % data['cursor']['estimatedResultCount'])
  hits = data['results']
  print('Top %d hits:' % len(hits))
  for h in hits: print(' ', h['url'])
  print('For more results, see %s' % data['cursor']['moreResultsUrl'])

showsome('eagles', 'love will keep us alive')

