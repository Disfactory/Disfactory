<template>
  <div id="app">
    <OSM />
    <app-button>確認</app-button>
    <app-text-field
      v-model="factoryName"
      placeholder="請輸入工廠名稱"
    />
    <app-select
      v-model="factoryType"
      :items="factoryTypeItems"
    />
  </div>
</template>

<script lang="ts">
import OSM from '@/components/OSM.vue'
import AppButton from '@/components/AppButton.vue'
import AppTextField from '@/components/AppTextField.vue'
import AppSelect from '@/components/AppSelect.vue'
import { createComponent, ref } from '@vue/composition-api'

export default createComponent({
  name: 'App',
  components: {
    OSM,
    AppButton,
    AppTextField,
    AppSelect
  },
  setup () {
    const factoryName = ref('')
    const factoryType = ref(0)
    const factoryTypeItems = [
      { text: '請選擇工廠類型', value: 0 },
      { text: '高危險', value: 1 },
      { text: '低危險', value: 2 }
    ]

    return {
      factoryName,
      factoryType,
      factoryTypeItems
    }
  }
})
</script>

<style lang="scss">
@import '~@/styles/index';
</style>
