<template>
  <div class="page-container">
    <div class="navbar-container">
      <app-navbar :dark="false" :fixed="true" @back="close">新增資訊</app-navbar>
    </div>
    <div class="page">
      <h1>輸入資訊</h1>

      <h3>工廠地點</h3>

      <div class="flex justify-between">
        <div class="flex flex-column flex-auto">
          <h3>工廠照片*</h3>
          <label>
            <small>請上傳至少一張照片</small>
          </label>
        </div>
        <div>
          <app-button>新增</app-button>
        </div>
      </div>

      <h3>工廠名稱</h3>
      <app-text-field
        v-model="factoryName"
        placeholder="請輸入工廠名稱"
      />

      <h3>工廠類型</h3>
      <app-select
        v-model="factoryType"
        :items="factoryTypeItems"
      />

      <h3>新增其它資訊</h3>
      <app-text-field
        v-model="factoryDescription"
        placeholder="請填入其他資訊，如聲音、氣味等等。"
      />

      <div class="text-center width-auto" style="margin-top: 60px; margin-bottom: 55px;">
        <app-button>送出</app-button>
      </div>

    </div>
  </div>
</template>

<script lang="ts">
import { createComponent, onMounted, ref } from '@vue/composition-api'
import AppButton from '@/components/AppButton.vue'
import AppTextField from '@/components/AppTextField.vue'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSelect from '@/components/AppSelect.vue'

export default createComponent({
  name: 'FormPage',
  components: {
    AppButton,
    AppTextField,
    AppSelect,
    AppNavbar
  },
  props: {
    close: {
      type: Function
    }
  },
  setup (props) {
    const factoryName = ref('')
    const factoryType = ref(0)
    const factoryTypeItems = [
      { text: '請選擇工廠類型', value: 0 },
      { text: '高危險', value: 1 },
      { text: '低危險', value: 2 }
    ]
    const factoryDescription = ref('')

    return {
      factoryName,
      factoryType,
      factoryTypeItems,
      factoryDescription,
      containerStyle: {
        width: '100%'
      }
    }
  }
})
</script>

<style lang="scss" scoped>
@import '../styles/utils';
@import '../styles/page';

.navbar-container {
  position: absolute;
  top: -47px;
  left: 0;
  z-index: 2;
}
</style>
