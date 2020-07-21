<template>
  <v-container class="image-upload-form">
    <h2 class="mb-2">上傳工廠照片</h2>

    <p>請至少上傳一張工廠照片。</p>

    <h3>工廠照片</h3>

    <v-btn :disabled="uploading">
      <label>
        <input multiple type="file" accept="image/*" ref="image" style="display: none;" @change="onChange" :disabled="uploading">
          新增照片
      </label>
    </v-btn>

    {{ JSON.stringify(previewImages) }}

    <hr>

    <h2>聯絡資訊（非必填）</h2>

    <p>
      如果對於照片有疑問，<br>
      我們會透過以下提供的資訊聯絡你。<br>
      如不願揭露自己身份，可跳過不填。
    </p>

    <v-text-field
      outlined
      placeholder="例：林先生、林小姐"
    ></v-text-field>

    <v-text-field
      outlined
      placeholder="例：abc@email.com、0920-123456"
    ></v-text-field>

    <v-container class="bottom-button-container d-flex justify-center">
      <v-btn x-large rounded @click="onSubmit" :disabled="!valid">
        下一步
      </v-btn>
    </v-container>
  </v-container>
</template>

<script lang="ts">
import { PropType } from 'vue'
import { createComponent } from '@vue/composition-api'
export default createComponent({
  props: {
    previewImages: {
      type: Array,
      default: []
    },
    uploading: {
      default: false
    },
    error: {
      default: null
    },
    onClickRemoveImage: {
      type: Function
    },
    submit: {
      type: Function,
    },
    valid: {
      type: Boolean,
      default: false
    }
  },
  name: 'ImageUploadForm',
  setup (props, context) {
    return {
      images: [],
      onChange: function (e: InputEvent) {
        context.emit('input', (e.target as HTMLInputElement).files)
      },
      onSubmit () {
        if (props.valid && typeof props.submit === 'function') {
          props.submit()
        }
      }
    }
  }
})
</script>

<style lang="scss" scoped>
.image-upload-form {
  @import '@/styles/typography.scss';

  background-color: white;
  z-index: 1;
  position: absolute;
  height: 100%;

  padding-bottom: 50px;
  overflow-y: auto;
  overflow-x: hidden;
}

.bottom-button-container {
  background: white;
  position: fixed;
  bottom: 0;
  left: 0;
  padding: 10px 15px;
}
</style>
G
