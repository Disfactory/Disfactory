<template>
  <nav :class="{ dark, fixed, hide }">
    <div class="back-button" @click="onBackClick()" v-show="!dark" data-label="navbar-back">
      <span />
      <span />
      <span />
    </div>
    <div class="back-placeholder" v-show="dark" />
    <slot />
    <div class="menu-button" @click="onMenuClick()" data-label="navbar-menu">
      <span />
      <span />
      <span />
    </div>
  </nav>
</template>

<script lang="ts">
import { createComponent } from '@vue/composition-api'

export default createComponent({
  name: 'AppNavbar',
  props: {
    dark: {
      type: Boolean,
      default: true
    },
    fixed: {
      type: Boolean,
      default: false
    },
    back: {
      type: Function
    },
    hide: {
      type: Boolean,
      default: false
    }
  },
  setup (_, { emit }) {
    return {
      onBackClick () {
        emit('back')
      },
      onMenuClick () {
        emit('menu')
      }
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/components/back-button';

nav {
  width: 100%;

  color: $primary-color;

  user-select: none;
  font-size: 24px;
  text-align: center;
  background-color: $dark-font-color;

  padding: 11px 14.5px;

  box-shadow: 0 2px 3px 0 rgba(0, 0, 0, 0.5);

  display: flex;
  justify-content: space-between;
  align-items: center;

  &.dark {
    background-color: $primary-color;
    color: $dark-font-color;

    .menu-button {
      span:nth-child(1) {
        border-color: $second-color;
      }

      span:nth-child(2), span:nth-child(3) {
        border-color: white;
        background-color: $second-color;
      }
    }
  }

  &.fixed {
    position: fixed;
    -webkit-overflow-scrolling: touch;
    top: 0;
    z-index: 7;
  }

  &.hide {
    display: none;
  }
}

.menu-button {
  width: 30px;
  height: 25px;
  position: relative;
  cursor: pointer;

  span {
    position: absolute;
    width: 100%;
    height: 5px;
    border-radius: 10px;
    background-color: $second-color;

    left: 0;
    border: solid 1px $second-color;
  }

  span:nth-child(1) {
    background-color: white;
  }

  span:nth-child(2) {
    top: 10px;
  }

  span:nth-child(3) {
    top: 20px;
  }
}

.back-placeholder {
  width: 30px;
  height: 30px;
}
</style>
