<template>
  <nav :class="{ dark, fixed }">
    <div class="back-button" @click="onBackClick()" v-show="!dark">
      <span />
      <span />
      <span />
    </div>
    <div class="back-placeholder" v-show="dark" />
    <slot />
    <div class="menu-button" @click="onMenuClick()">
      <span />
      <span />
      <span />
    </div>
  </nav>
</template>

<script lang="ts">
import { createComponent, PropType, computed } from '@vue/composition-api'

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
    }
  },
  setup ({ back }, { emit }) {
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
  }

}

.back-button {
  width: 30px;
  height: 20px;
  position: relative;
  cursor: pointer;

  span {
    position: absolute;
    width: 100%;
    height: 4px;
    border-radius: 5px;
    background-color: $primary-color;

    left: 0;
  }

  span:nth-child(1) {
    top: 7px;
  }
  span:nth-child(2) {
    transform: rotate(-45deg);
    width: 65%;
    top: 1px;
    left: -4px;
  }
  span:nth-child(3) {
    transform: rotate(45deg);
    width: 65%;
    top: 12px;
    left: -4px;
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
