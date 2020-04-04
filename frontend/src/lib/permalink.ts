// https://github.com/teia-tw/drinking_water/blob/f2fe7962bf9a48438eec5068e8bfe8b320f5b7e7/app.js#L6-L36

type PermaLinkState = {
  lat?: number,
  lng?: number,
  zoom?: number
}
const fields: (keyof PermaLinkState)[] = ['lat', 'lng', 'zoom']

type KeyFn<T> = { [P in keyof Required<T>]: () => number | void }

export const permalink = new class implements KeyFn<PermaLinkState> {
  s: PermaLinkState = {}

  load (loc: Location) {
    const m = /^#map=([\d.]+)\/([\d.]+)\/([\d.]+)$/.exec(loc.hash)
    if (m !== null) {
      this.s.zoom = parseFloat(m[1])
      this.s.lat = parseFloat(m[2])
      this.s.lng = parseFloat(m[3])
    }
  }

  dumps () {
    if (fields.some(f => typeof this.s[f] === 'undefined')) {
      return ''
    }
    return `#map=${this.s.zoom?.toFixed(2)}/${this.s.lat}/${this.s.lng}`
  }

  defineGetterSetter (key: keyof PermaLinkState) {
    return (...args: number[]) => {
      if (args.length > 0) {
        this.s[key] = args[0]
      }
      return this.s[key]
    }
  }

  lng = this.defineGetterSetter('lng')
  lat = this.defineGetterSetter('lat')
  zoom = this.defineGetterSetter('zoom')
}()
