<template>
  <div :class="{ base: true, open: value }" @click="close" data-label="sidebar-close">
    <div :class="{ sidebar: true, open: value }">
      <div class="close" @click="close" data-label="sidebar-close" />
      <h1>主選單</h1>
      <hr />
      <ul>
        <li v-for="(link,index) in links" :key="index">
          <a @click.stop="onClick(link)" :data-label="`sidebar-${link.text}`" :href="getHref(link)" :target="getTarget(link)">{{ link.text }}</a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { createComponent, ref } from '@vue/composition-api'
import { useModalState } from '../lib/hooks'

export default createComponent({
  name: 'AppSidebar',
  props: {
    value: {
      type: Boolean,
      required: true
    }
  },
  setup (_, context) {
    const [, modalActions] = useModalState()
    const links = [
      { text: '使用說明', action: modalActions.openTutorialModal },
      { text: '安全須知', action: modalActions.openSafetyModal },
      { text: '聯絡我們', action: modalActions.openContactModal },
      { text: '常見問題', href: 'https://about.disfactory.tw/#section-f_c360c8de-447e-4c0a-a856-4af18b9a5240' },
      { text: '關於舉報系統', href: 'https://about.disfactory.tw' },
      { text: '問題回報', href: 'https://airtable.com/shrUraKakZRpH52DO' }
    ]
    const close = () => {
      context.emit('input', false)
    }

    return {
      links,
      close,
      onClick: (link) => {
        if (typeof link.action === 'function') {
          link.action()
        }
      },
      getHref: (link) => {
        return link.href
      },
      getTarget: (link) => {
        if (typeof link.href === 'string') {
          return '_blank'
        } else {
          return null
        }
      }
    }
  }
})
</script>

<style lang="scss" scoped>
@import '~@/styles/utils';

.base {
  position: fixed;
  -webkit-overflow-scrolling: touch;
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
    -webkit-overflow-scrolling: touch;
    top: 0;
    right: 0;
    bottom: 0;
    width: 90%;
    z-index: 10;
    max-width: 400px;
    color: #fff;
    background-color: #6d8538;
    padding: 60px 30px 20px 30px;
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
      width: 60%;
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
          cursor: pointer;
          user-select: none;
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
