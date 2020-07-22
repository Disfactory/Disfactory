<template>
  <div class="confirm-factory-page">
    <h2 class="mt-2 mb-2">確認及補充工廠資訊</h2>

    <p>請確認工廠地點及照片，並補充工廠資訊。</p>

    <h3 class="mt-2 mb-2 required">工廠地點</h3>

    <p>
      返回<a href="#">步驟一</a>編輯
    </p>

    <h3 class="mt-2 mb-2 required">工廠照片</h3>

    {{ JSON.stringify(previewImages) }}

    <h3 class="mt-2 mb-2 required">聯絡人暱稱</h3>

    <p>{{ formState.nickname }}</p>

    <h3 class="mt-2 mb-2 required">聯絡方式 (email或電話)</h3>

    <p>{{ formState.contact }}</p>
  </div>
</template>

<script lang="ts">
import { createComponent } from '@vue/composition-api'

export default createComponent({
  name: 'ConfirmFactory',
  props: {
    formState: {
      type: Object,
      default: {}
    },
    previewImages: {
      type: Array,
      default: []
    }
  }
})
</script>

<style lang="scss" scoped>
.confirm-factory-page {
  @import '@/styles/typography.scss';

  background-color: white;
  z-index: 1;
  position: absolute;
  width: 100%;
  height: 100%;

  padding-bottom: 50px;
  overflow-y: auto;
  overflow-x: hidden;

  padding: 20px 15px;
}

</style>
G
