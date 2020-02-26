// eslint-disable-next-line @typescript-eslint/prefer-regexp-exec
export const isiOS = !!(navigator.userAgent.match(/(iPod|iPhone|iPad)/) && navigator.userAgent.match(/AppleWebKit/))

export const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent)
