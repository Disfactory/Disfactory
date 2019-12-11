/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-non-null-assertion */
type PixelMapper = (data: Uint8ClampedArray) => void

const canvas = (window.OffscreenCanvas) ? new OffscreenCanvas(500, 500) : document.createElement('canvas')
const ctx = canvas.getContext('2d')!

export const createImageProcessor = (processor: PixelMapper) => (src: string): Promise<string> => {
  return new Promise((resolve) => {
    const image = new Image()
    image.crossOrigin = ''
    image.src = src
    image.style.display = 'none'
    image.onload = async () => {
      canvas.width = image.width
      canvas.height = image.height
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      ctx.drawImage(image, 0, 0)

      const imageData = ctx.getImageData(0, 0, image.width, image.height)
      const { data } = imageData

      await Promise.resolve(processor(data))

      const tmpCanvas = document.createElement('canvas')
      const tmpCtx = tmpCanvas.getContext('2d')!
      tmpCanvas.width = image.width
      tmpCanvas.height = image.height

      tmpCtx.putImageData(imageData, 0, 0)

      resolve(tmpCanvas.toDataURL())

      image.remove()
      tmpCanvas.remove()
    }
  })
}

export const toGrayScale = createImageProcessor(data => {
  // doing grayscale operaion pixel by pixel
  for (let i = 0; i < data.length; i += 4) {
    const avg = (data[i] + data[i + 1] + data[i + 2]) / 3
    data[i] = avg // red
    data[i + 1] = avg // green
    data[i + 2] = avg // blue
  }
})

const argriculturalLandColors = [
  [255, 241, 0]
]

const isArrayEqual = (a: Array<any>, b: Array<any>) => !a.some((v, i) => b[i] !== v)

const isArgriculturalLand = (arr: Array<any>) => argriculturalLandColors.some(c => isArrayEqual(c, arr))

export const flipArgriculturalLand = createImageProcessor(data => {
  for (let i = 0; i < data.length; i += 4) {
    const color = Array.from(data.slice(i, i + 3))

    if (isArgriculturalLand(color)) {
      // set to transparent
      data[i] = 0
      data[i + 1] = 0
      data[i + 2] = 0
      data[i + 3] = 1
    } else {
      // set to black
      data[i] = 0
      data[i + 1] = 0
      data[i + 2] = 0
      data[i + 3] = 255
    }
  }
})
