<template>
  <div id="app">
    <app-navbar>農地違章工廠舉報</app-navbar>
    <filter-modal :open="filterModalOpen" :dismiss="closeFilterModal" />
    <OSM />
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
import AppNavbar from '@/components/AppNavbar.vue'
import FilterModal from '@/components/FilterModal.vue'
import { createComponent, ref } from '@vue/composition-api'

export default createComponent({
  name: 'App',
  components: {
    OSM,
    AppButton,
    AppTextField,
    AppSelect,
    AppNavbar,
    FilterModal
  },
  setup () {
    const factoryName = ref('')
    const factoryType = ref(0)
    const factoryTypeItems = [
      { text: '請選擇工廠類型', value: 0 },
      { text: '高危險', value: 1 },
      { text: '低危險', value: 2 }
    ]
    const filterModalOpen = ref(false)
    const closeFilterModal = () => {
      filterModalOpen.value = false
    }

    return {
      factoryName,
      factoryType,
      factoryTypeItems,

      filterModalOpen,
      closeFilterModal
    }
  }
})
</script>

<style lang="scss">
@import '~@/styles/index';
</style>
