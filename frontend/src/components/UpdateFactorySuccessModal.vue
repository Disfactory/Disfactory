<template>
  <app-modal :open="open" :dismiss="dismiss" :showCloseButon="false">
    <h3>感謝您補充資訊！</h3>
    <app-button @click="dismiss" data-label="update-factory-success-apply">確認</app-button>
  </app-modal>
</template>

<script lang="ts">
import AppModal from '@/components/AppModal.vue'
import AppButton from '@/components/AppButton.vue'
import { createComponent } from '@vue/composition-api'

export default createComponent({
  name: 'UpdateFactorySuccessModal',
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

<style lang="scss" scoped>
@import '@/styles/variables';

h3 {
  color: $second-color;
  font-size: 24px;
}
</style>
