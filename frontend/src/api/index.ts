import axios from 'axios'
import { FactoryPostData, FactoryData, FactoriesResponse, FactoryImage } from '@/types'
import EXIF from '@disfactory/exif-js'

const baseURL = process.env.NODE_ENV === 'production' ? process.env.VUE_APP_BASE_URL : '/server/api'

const instance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json'
  }
})

type ImageResponse = {
  token: string
}

export type UploadedImages = {
  token: string,
  src: string // used for preview images
}[]

export async function getFactories (range: number, lng: number, lat: number): Promise<FactoriesResponse> {
  try {
    const { data } = await instance.get(`/factories?range=${range}&lng=${lng}&lat=${lat}`)
    return data
  } catch (err) {
    console.error(err)
    throw new TypeError('Get factory failed')
  }
}

const IMGUR_CLIENT_ID = '39048813b021935'

async function uploadToImgur (file: File) {
  const formData = new FormData()
  formData.append('image', file)

  const { data } = await axios({
    method: 'POST',
    url: 'https://api.imgur.com/3/image',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
      Authorization: `Client-ID ${IMGUR_CLIENT_ID}`
    }
  })

  return {
    link: data.data.link as string,
    file
  }
}

const convertTurple2Number = (input: [number, number, number]) => input[0] + (input[1] / 60) + (input[2] / 3600)

type ExifData = { DateTimeOriginal?: string, GPSLatitude?: [number, number, number], GPSLongitude?: [number, number, number] }
type AfterExifData = { Latitude?: number, Longitude?: number, DateTimeOriginal?: string }

function readImageExif (file: File): Promise<AfterExifData> {
  const fileReader = new FileReader()
  return new Promise((resolve) => {
    fileReader.onload = (e: ProgressEvent<FileReader>) => {
      if (!e.target) {
        resolve({})
        return
      }
      const data: ExifData = EXIF.readFromBinaryFile(e.target.result)

      const result: AfterExifData = {}
      if (data.GPSLatitude) {
        result.Latitude = convertTurple2Number(data.GPSLatitude)
      }
      if (data.GPSLongitude) {
        result.Longitude = convertTurple2Number(data.GPSLongitude)
      }
      if (data.DateTimeOriginal) {
        result.DateTimeOriginal = data.DateTimeOriginal
      }

      resolve(result)
    }
    fileReader.readAsArrayBuffer(file)
  })
}

export type UploadedImage = {
  token: string,
  src: string
}

async function uploadExifAndGetToken ({ link, file }: { link: string, file: File }) {
  const exifData = await readImageExif(file)
  const { data }: { data: ImageResponse } = await instance.post('/images', { url: link, ...exifData })

  return {
    token: data.token,
    src: URL.createObjectURL(file)
  } as UploadedImage
}

export async function uploadImages (files: FileList): Promise<UploadedImages> {
  return Promise.all(
    Array.from(files).map((file) => uploadToImgur(file).then((el) => uploadExifAndGetToken(el)))
  )
}

export async function updateFactoryImages (factoryId: string, files: FileList, { nickname, contact }: { nickname?: string, contact?: string }) {
  return Promise.all(
    Array.from(files).map((file) => uploadToImgur(file).then((el) => (async () => {
      const exifData = await readImageExif(el.file)
      const { data }: { data: FactoryImage } = await instance.post(`/factories/${factoryId}/images`, { url: el.link, ...exifData, nickname, contact })
      // eslint-disable-next-line @typescript-eslint/camelcase
      data.image_path = el.link
      return data
    })()))
  )
}

export async function createFactory (factory: FactoryPostData): Promise<FactoryData> {
  try {
    const { data }: { data: FactoryData } = await instance.post('/factories', JSON.stringify(factory))

    return data
  } catch (err) {
    console.error(err)
    throw new TypeError('Create factory failed')
  }
}

// !FIXME: add more factory fields
type UpdatableFactoryFields = {
  name: string,
  nickname: string,
  contact: string,
  others: string,
  images: string[]
}

export async function updateFactory (factoryId: string, factoryData: Partial<UpdatableFactoryFields>): Promise<FactoryData> {
  try {
    const { data }: { data: FactoryData } = await instance.put(`/factories/${factoryId}`, JSON.stringify(factoryData))

    return data
  } catch (err) {
    console.error(err)
    throw new TypeError('Update factory failed')
  }
}
