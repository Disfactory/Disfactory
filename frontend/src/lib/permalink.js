// https://github.com/teia-tw/drinking_water/blob/f2fe7962bf9a48438eec5068e8bfe8b320f5b7e7/app.js#L6-L36

const fields = ['zoom', 'lat', 'lng']

export const permalink = (function () {
  var permalink = {}
  var s = {
    lat: undefined,
    lng: undefined,
    zoom: undefined
  }
  permalink.load = function (loc) {
    var m = loc.hash.match(/^#map=([\d\.]+)\/([\d\.]+)\/([\d\.]+)$/)
    if (m !== null) {
      s.zoom = parseFloat(m[1])
      s.lat = parseFloat(m[2])
      s.lng = parseFloat(m[3])
    }
  }

  permalink.dumps = function () {
    if (fields.some(f => typeof s[f] === 'undefined' || isNaN(s[f]))) {
      return ''
    }
    return '#map=' + s.zoom + '/' + s.lat + '/' + s.lng
  }

  fields.forEach(function (n) {
    permalink[n] = function () {
      if (arguments.length > 0) {
        s[n] = arguments[0]
      }
      return s[n]
    }
  })
  return permalink
})()
