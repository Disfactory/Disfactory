<template>
  <div class="getting-started-container">
    <app-modal :open="open" :showCloseButton="false" :dismiss="dismiss">
      <div class="page">
        <h3>嗨你好，歡迎來到農地違章工廠回報行動！</h3>
        <p>需要大家協助回報以下資訊：</p>

        <ul>
          <li>中高污染工廠</li>
          <li>105.05.20 後新建的違章工廠</li>
        </ul>

        <p>大家的回報會由地球公民基金會彙整追蹤後向政府舉報。</p>

        <small>
          行動前請同意資料貢獻<a href="https://license.disfactory.tw/#%E8%BE%B2%E5%9C%B0%E9%81%95%E7%AB%A0%E5%B7%A5%E5%BB%A0%E5%9B%9E%E5%A0%B1%E7%B3%BB%E7%B5%B1%EF%BC%88disfactory%EF%BC%89%E8%B2%A2%E7%8D%BB%E5%8D%94%E8%AD%B0" target="_blank">授權條款</a>與<a href="https://license.disfactory.tw/#%E9%9A%B1%E7%A7%81%E6%AC%8A%E6%A2%9D%E6%AC%BE" target="_blank">隱私條款</a>。本網站由<a href="https://www.cet-taiwan.org/" target="_blank">地球公民基金會</a>與 <a href="https://g0v.tw/" target="_blank">g0v.tw</a> 社群共同開發。
        </small>

        <app-button @click="agree">我同意加入回報</app-button>

        <small>
          <a href="https://about.disfactory.tw">我不同意，請帶我離開這個頁面</a>
        </small>
      </div>
    </app-modal>
  </div>
</template>

<script lang="ts">
import AppModal from '@/components/AppModal.vue'
import AppButton from '@/components/AppButton.vue'
import { createComponent } from '@vue/composition-api'

export default createComponent({
  name: 'GettingStartedModal',
  components: {
    AppModal,
    AppButton
  },
  props: {
    open: {
      type: Boolean,
      default: false
    },
    dismiss: {
      type: Function
    }
  },
  setup (props) {
    return {
      agree () {
        localStorage.setItem('use-app', 'true')
        if (props.dismiss) {
          props.dismiss()
        }
      }
    }
  }
})
</script>

<style lang="scss">
@import '@/styles/page';
@import '@/styles/variables';

.getting-started-container .app-modal {
  top: 20px;
  max-height: calc(100% - 40px);
  max-width: calc(100% - 20px);
  padding-top: 35px;

  .page {
    h3 {
      color: $primary-color;
      font-size: 16px;
      margin-top: 0;
      line-height: 1.2;
    }

    small {
      text-align: center;
      display: block;
      margin: 1em 0;
      line-height: 1.1;
    }

    a {
      color: $primary-color;
      text-decoration: none;
    }

    pre {
      line-height: 1.5em;
      white-space: pre-line;
    }
  }
}
</style>
