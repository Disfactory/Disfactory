<template>
  <div class="app-modal-component"
    :class="{ open }"
  >
    <div class="app-modal-backdrop" @click="dismiss" />
    <div class="app-modal">
      <div class="close" @click="dismiss" v-if="showCloseButon" />
      <slot />
    </div>
  </div>
</template>

<script lang="ts">
import { createComponent } from '@vue/composition-api'

export default createComponent({
  name: 'AppModal',
  props: {
    open: {
      type: Boolean,
      default: false
    },
    dismiss: {
      type: Function
    },
    showCloseButon: {
      type: Boolean,
      default: true
    }
  }
})
</script>

<style lang="scss" scoped>
@import '../styles/variables';
@import '~@/styles/utils';

.app-modal-component {
  z-index: 997;
  position: fixed;
  -webkit-overflow-scrolling: touch;

  justify-content: center;
  align-items: center;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;

  padding: 45px 16px;

  display: none;

  &.open {
    display: flex;
  }
}

.app-modal-backdrop {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 998;
}

.app-modal {
  z-index: 999;

  border-radius: 3px;
  border: solid 2px $primary-color;
  background-color: $background-color;

  padding: 27px 22px;

  position: absolute;
  -webkit-overflow-scrolling: touch;
  top: 90px;
  max-height: 100%;
  max-width: 100%;
  overflow: auto;

  .close {
    z-index: 1;
    @include close-button;
  }
}
</style>
