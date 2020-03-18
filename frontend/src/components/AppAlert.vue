<template>
  <div class="app-alert" v-if="alert">
    <div class="close" @click="dismiss" data-label="alert-close" />
    <img src="/images/alert.svg" alt="alert">
    <div>
      <div class="alert-title">{{ alert.title }}</div>
      <p class="alert-descriptioin">{{ alert.dismissText }}</p>
    </div>
  </div>
</template>

<script lang="ts">
import AppModal from '@/components/AppModal.vue'
import { createComponent } from '@vue/composition-api'

export default createComponent({
  name: 'AppAlert',
  props: {
    alert: {
      type: Object
    },
    dismiss: {
      type: Function
    }
  }
})
</script>

<style lang="scss" scoped>
@import '~@/styles/utils';

.app-alert {
  position: fixed;
  bottom: 0;
  width: 100%;
  background-color: rgba(0, 0, 0, 0.82);
  color: white;
  padding: 27px 23px 18px;

  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  z-index: 1;

  img {
    margin-right: 17px;
  }

  .alert-title {
    font-size: 18px;
    line-height: 20px;
    font-weight: 500;
    white-space: pre;
  }

  .alert-descriptioin {
    font-size: 12px;
  }

  .close {
    z-index: 2;
    @include close-button;

    top: 17px;
    right: 17px;

    &::before, &::after {
      background-color: white;
    }
  }
}
</style>
