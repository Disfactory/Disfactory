type PixelMapper = (data: Uint8ClampedArray) => void

export const createImageProcessor = (processor: PixelMapper) => (src: string) => {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')!

  return new Promise((resolve) => {
    const image = new Image()
    image.crossOrigin = ''
    image.src = src
    image.style.display = 'none'
    image.onload = async () => {
      canvas.width = image.width
      canvas.height = image.height

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
      canvas.remove()
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
