<template>
  <div class="ios-version-modal-container">
    <app-modal :open="open" :dismiss="dismiss">
      <div class="page">
        <h3>無法新增可疑工廠</h3>
        <p>iOS版本13.1, 13.2, 13.3無法使用此功能。請使用電腦新增可疑工廠或是更新iOS版本。</p>

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
