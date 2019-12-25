<template>
  <div class="contact-modal-container">
    <app-modal :open="open" :dismiss="dismiss">
      <div class="page">
        <img width="137" src="/images/cet-logo.png" alt="Citizen of the Earth Taiwan">

        <h3>
          有任何舉報相關問題<br>
          歡迎聯絡
        </h3>

        <p>
          地球公民基金會<br>
          TEL: 07-2156809<br>
          Email: <a href="mailto:cet@cet-taiwan.org">cet@cet-taiwan.org</a><br>
        </p>
      </div>
    </app-modal>
  </div>
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

<style lang="scss">
@import '@/styles/page';
@import '@/styles/variables';

.contact-modal-container .app-modal {
  top: 47px;
  max-height: calc(100% - 100px);
  margin: 0 7px;
  padding-top: 60px;

  .page {
    text-align: center;

    h3 {
      color: $primary-color;
      line-height: 1.5em;
    }
  }
}
</style>
