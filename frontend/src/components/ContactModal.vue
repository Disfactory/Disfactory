<template>
  <app-modal :open="open" :dismiss="dismiss">
    <div class="page">

    </div>
  </app-modal>
</template>

<script lang="ts">
import AppModal from '@/components/AppModal.vue'
import { createComponent } from '@vue/composition-api'

export default createComponent({
  name: 'ContactModal',
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

<style lang="scss" scoped>
@import '@/styles/page';

.page-inner {
  margin-bottom: 20px;
  padding: 0 10px;
}
</style>
