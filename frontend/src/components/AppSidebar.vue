<template>
  <div :class="{ base: true, open: value }">
    <div :class="{ sidebar: true, open: value }">
      <div class="close" @click="close" />
      <h1>主選單</h1>
      <hr />
      <ul>
        <li v-for="(link,index) in links" :key="index">
          <a :href="link.href">{{ link.text }}</a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { createComponent, ref } from '@vue/composition-api'

export default createComponent({
  name: 'AppSidebar',
  props: {
    value: {
      type: Boolean,
      required: true
    }
  },
  setup (_, context) {
    const links = ref([
      { text: '使用教學', href: '#' },
      { text: '安全須知', href: '#' },
      { text: '聯絡我們', href: '#' },
      { text: '關於舉報系統', href: '#' }
    ])
    const close = () => {
      context.emit('input', false)
    }

    return {
      links,
      close
    }
  }
})
</script>

<style lang="scss" scoped>
@import '~@/styles/utils';

.base {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 9;
  background-color: rgba(#000000, 0.4);
  visibility: hidden;
  opacity: 0;
  transition: all 0.5s cubic-bezier(.4,0,.2,1);

  .sidebar {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    width: 90%;
    z-index: 10;
    max-width: 400px;
    color: #fff;
    background-color: #6d8538;
    padding: 60px 120px 20px 30px;
    transform: translateX(100%);
    opacity: 0;
    transition: all 0.5s cubic-bezier(.4,0,.2,1);

    > * {
      margin: 16px 0;
    }

    .close {
      @include close-button;
      right: unset;
      left: 30px;

      &::before, &::after {
        z-index: 11;
        background: #fff;
      }
    }

    h1 {
      font-size: 36px;
      line-height: 1.3;
    }

    hr {
      border: none;
      width: 100%;
      height: 1px;
      background-color: #ffffff;
    }

    ul {
      padding: 0;
      list-style: none;

      li {
        a {
          color: #fff;
          font-size: 24px;
          line-height: 2;
          text-decoration: none;
        }
      }
    }
  }

  .sidebar.open {
    opacity: 1;
    transform: translateX(0);
  }
}

.base.open {
  visibility: visible;
  opacity: 1;
}
</style>
