<template>
  <div class="getting-started-container">
    <app-modal :open="open" :dismiss="dismiss">
      <div class="page">
        <p>
          準備好要開始檢舉農地違章工廠了嗎？請點選右上角主選單 <img width="30" src="/images/menu-pic.png">，了解如何檢舉及相關安全須知！
        </p>
      </div>
    </app-modal>
  </div>
</template>

<script lang="ts">
import AppModal from '@/components/AppModal.vue'
import { createComponent } from '@vue/composition-api'

export default createComponent({
  name: 'GettingStartedModal',
  components: {
    AppModal
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

.getting-started-container .app-modal {
  top: 47px;
  max-height: calc(100% - 100px);
  margin: 0 7px;
  padding-top: 70px;

  .page h3 {
    color: $primary-color;
  }
}
</style>
