// eslint-disable-next-line @typescript-eslint/prefer-regexp-exec
export const isiOS = !!(navigator.userAgent.match(/(iPod|iPhone|iPad)/) && navigator.userAgent.match(/AppleWebKit/))

export const isSafari = /constructor/i.test(window.HTMLElement) || (function (p) { return p.toString() === '[object SafariRemoteNotification]' })(!window.safari || (typeof window.safari !== 'undefined' && window.safari.pushNotification))
