<template>
  <app-modal :open="open" :dismiss="dismiss" class="page">
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
      v-model="title"
      placeholder="例：林先生"
    />

    <h3>聯絡資料</h3>
    <app-text-field
      v-model="phone"
      placeholder="例：0912345678"
    />

    <div style="margin-top: 35px;">
      <app-button @click="handleImagesUpload()">上傳照片</app-button>
    </div>
  </app-modal>
</template>

<script lang="ts">
import AppModal from '@/components/AppModal.vue'
import AppButton from '@/components/AppButton.vue'
import AppTextField from '@/components/AppTextField.vue'
import { createComponent, reactive, ref, computed } from '@vue/composition-api'
import { uploadImages } from '../api'

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
    }
  },
  setup (props, context) {
    const title = ref('')
    const phone = ref('')

    const imageUrls = computed(() => {
      const urls = []
      for (let i = 0; i < props.images!.length; i++) {
        urls.push(URL.createObjectURL(props.images![i]))
      }

      return urls
    })

    return {
      title,
      phone,
      imageUrls,
      async handleImagesUpload () {
        const images = await uploadImages(props.images!)
        props.finishImagesUpload(images)

        // TODO: decorate dismiss method, clear images when dismiss
        props.dismiss()
      }
    }
  }
})
</script>

<style lang="scss" scoped>
@import '../styles/page';
@import '../styles/images-grid';
</style>
