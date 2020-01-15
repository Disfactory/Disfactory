import axios from 'axios'
import { FactoryPostData, FactoryData, FactoriesResponse, FactoryImage } from '@/types'

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

export async function uploadImages (files: FileList): Promise<UploadedImages> {
  const results: UploadedImages = []

  for (const file of files) {
    const formData = new FormData()
    formData.append('image', file)

    const { data }: { data: ImageResponse } = await instance.post('/images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    // TODO: error handling

    results.push({
      token: data.token,
      src: URL.createObjectURL(file)
    })
  }

  return results
}

export async function updateFactoryImages (factoryId: string, files: FileList, { nickname, contact }: { nickname?: string, contact?: string }) {
  const results: FactoryImage[] = []

  for (const file of files) {
    const formData = new FormData()
    formData.append('image', file)

    if (nickname) {
      formData.append('nickname', nickname)
    }
    if (contact) {
      formData.append('contact', contact)
    }

    const { data }: { data: FactoryImage } = await instance.post(`/factories/${factoryId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    results.push(data)
  }

  return results
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
