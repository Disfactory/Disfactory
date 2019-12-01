import axios from 'axios'

const instance = axios.create({
  baseURL: '/server/api'
})

type ImageResponse = {
  token: string;
}

export type UploadedImages = {
  token: string;
  src: string; // used for preview images
}[]

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
