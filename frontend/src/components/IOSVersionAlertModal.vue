<template>
  <div class="ios-version-modal-container">
    <app-modal :open="open" :dismiss="dismiss">
      <div class="page">
        <h3>⚠️你的手機無法新增可疑工廠</h3>
        <p>
          很抱歉，你的 iPhone iOS 操作系統無法成功在本網站上傳照片。<br>
          請改用電腦新增可疑工廠照片或是至「系統設定」升級 iOS操作系統版本到至少 13.4 以上。瀏覽地圖功能則不受影響。
        </p>
        <app-button @click="dismiss">知道了</app-button>
      </div>
    </app-modal>
  </div>
</template>

<script lang="ts">
import AppModal from '@/components/AppModal.vue'
import AppButton from '@/components/AppButton.vue'
import { createComponent } from '@vue/composition-api'

export default createComponent({
  name: 'IosVersionModal',
  components: {
    AppModal,
    AppButton
  },
  props: {
    open: {
      type: Boolean,
      default: false
    },
    dismiss: {
      type: Function
    }
  }
})
</script>

<style lang="scss">
@import '@/styles/page';
@import '@/styles/variables';

.ios-version-modal-container .app-modal {
  top: 25px;
  max-height: calc(100% - 50px);
  max-width: calc(100% - 20px);
  padding-top: 60px;

  .page {

    h3 {
      color: $primary-color;
      line-height: 1.5em;
    }
  }
}
</style>
