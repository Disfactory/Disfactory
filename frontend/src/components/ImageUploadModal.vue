<template>
  <app-modal :open="open" :dismiss="closeModal" class="page">
    <h2>工廠照片</h2>

    <div class="images-grid">
      <div class="image-card" :key="url" v-for="url in imageUrls" >
        <img :src="url" />
      </div>
    </div>

    <h2>
      聯絡資訊（非必填）<br>
      <small style="font-size: 14px;">如果對於照片有疑問，我們會透過您提供的資訊聯絡你。</small>
    </h2>

    <h3>稱呼</h3>
    <app-text-field
      v-model="formState.nickname"
      placeholder="例：林先生"
    />

    <h3>聯絡資料</h3>
    <app-text-field
      v-model="formState.contact"
      placeholder="例：0912345678"
    />

    <div style="margin-top: 35px;">
      <app-button @click="handleImagesUpload()" :disabled="formState.uploading">
        {{ formState.uploading ? '上傳中' : '上傳照片' }}
      </app-button>
    </div>
  </app-modal>
</template>

<script lang="ts">
import AppModal from '@/components/AppModal.vue'
import AppButton from '@/components/AppButton.vue'
import AppTextField from '@/components/AppTextField.vue'
import { createComponent, computed, reactive } from '@vue/composition-api'
import { uploadImages, updateFactoryImages } from '../api'

export default createComponent({
  name: 'FilterModal',
  components: {
    AppModal,
    AppButton,
    AppTextField
  },
  props: {
    open: {
      type: Boolean,
      default: false
    },
    dismiss: {
      type: Function,
      required: true
    },
    images: {
      type: FileList
    },
    finishImagesUpload: {
      type: Function,
      required: true
    },
    finishUploaderForm: {
      type: Function,
      required: true
    },
    mode: {
      type: String,
      required: true,
      defaultValue: 'create'
    },
    factoryData: {
      type: Object,
      required: true
    }
  },
  setup (props) {
    const formState = reactive({
      nickname: '',
      contact: '',
      uploading: false
    })

    const imageUrls = computed(() => {
      const urls = []
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      for (let i = 0; i < props.images!.length; i++) {
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        urls.push(URL.createObjectURL(props.images![i]))
      }

      return urls
    })

    return {
      formState,
      imageUrls,
      async handleImagesUpload () {
        formState.uploading = true

        if (props.mode === 'create') {
          try {
            // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
            const images = await uploadImages(props.images!)
            props.finishUploaderForm(formState.nickname, formState.contact)
            await props.finishImagesUpload(images, imageUrls)

            formState.uploading = false

            props.dismiss()
          } catch (err) {
            formState.uploading = false

            // TODO: show me some error
            console.error(err)
          }
        } else {
          // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
          const images = await updateFactoryImages(props.factoryData.id, props.images!, {
            nickname: formState.nickname,
            contact: formState.contact
          })
          props.finishUploaderForm(formState.nickname, formState.contact)
          await props.finishImagesUpload(images, [])

          formState.uploading = false
          props.dismiss()
        }
      },
      closeModal () {
        if (!formState.uploading) {
          props.finishImagesUpload([])
          props.finishUploaderForm('', '')
          props.dismiss()
        }
      }
    }
  }
})
</script>

<style lang="scss" scoped>
@import '../styles/page';
@import '../styles/images-grid';
</style>
