// eslint-disable-next-line @typescript-eslint/prefer-regexp-exec
export const isiOS = !!(navigator.userAgent.match(/(iPod|iPhone|iPad)/) && navigator.userAgent.match(/AppleWebKit/))

export const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent)

export function iOSversion () {
  if (/iP(hone|od|ad)/.test(navigator.platform)) {
    /* eslint-disable-next-line @typescript-eslint/prefer-regexp-exec */
    const v = (navigator.appVersion).match(/OS (\d+)_(\d+)_?(\d+)?/)
    if (v) {
      return [parseInt(v[1], 10), parseInt(v[2], 10), parseInt(v[3] || '0', 10)].join('.')
    }
  }
}

export function isNotSupportedIOS () {
  let version
  /* eslint-disable-next-line @typescript-eslint/prefer-regexp-exec */
  return !!isiOS && !!(version = iOSversion()) && !!version.match(/^13\.(1|2|3)/)
}
