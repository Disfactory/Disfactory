import axios from 'axios'
import { FactoryPostData, FactoryData, FactoriesResponse } from '@/types'

const baseURL = process.env.NODE_ENV === 'production' ? 'https://middle2.disfactory.tw/api' : '/server/api'

const instance = axios.create({
  baseURL
})

type ImageResponse = {
  token: string;
}

export type UploadedImages = {
  token: string;
  src: string; // used for preview images
}[]

export async function getFactories (range: number, lng: number, lat: number): Promise<FactoriesResponse> {
  const { data } = await instance.get(`/factories?range=${range}&lng=${lng}&lat=${lat}`)

  return data
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

export async function createFactory (factory: FactoryPostData): Promise<FactoryData> {
  try {
    const { data }: { data: FactoryData } = await instance.post('/factories', JSON.stringify(factory), {
      headers: {
        'Content-Type': 'application/json'
      }
    })

    return data
  } catch (err) {
    console.error(err)
    throw new TypeError('Create factory failed')
  }
}
