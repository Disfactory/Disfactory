<template>
  <div class="getting-started-container">
    <app-modal :open="open" :dismiss="dismiss">
      <div class="page">
        <pre>
          嗨，歡迎來到農地違章工廠舉報小幫手！
          你回報的新增建違章工廠
          既有中高污染工廠
          會由地球公民基金會
          做案件追蹤
          向政府進行舉報

          使用教學在右上角<img width="30" src="/images/menu-pic.png">喔！

          本網站由地球公民基金會與 g0v 社群共同開發
        </pre>
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
  top: 20px;
  max-height: calc(100% - 100px);
  margin: 0 7px;
  padding-top: 70px;

  .page {
    h3 {
      color: $primary-color;
    }

    pre {
      line-height: 1.5em;
      white-space: pre-line;
    }
  }
}
</style>
