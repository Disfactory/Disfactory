<template>
  <app-modal :open="open">
    <h1>篩選</h1>
    <label>
      <input type="checkbox" name="F" v-model="filterF">
      資料不全
    </label>
    <label>
      <input type="checkbox" name="A" v-model="filterA">
      資料齊全
    </label>
    <label>
      <input type="checkbox" name="D" v-model="filterD">
      已舉報
    </label>
    <app-button @click="onClick()">確認</app-button>
  </app-modal>
</template>


<script lang="ts">
import AppModal from '@/components/AppModal.vue'
import AppButton from '@/components/AppButton.vue'
import { setFactoryStatusFilter } from '../lib/map'
import { createComponent, reactive, ref } from '@vue/composition-api'

export default createComponent({
  name: 'FilterModal',
  components: {
    AppModal,
    AppButton
  },
  props: {
    open: {
      type: Boolean,
      default: false
    }
  },
  setup (props, context) {
    const filterF = ref(false)
    const filterA = ref(false)
    const filterD = ref(false)

    return {
      filterF,
      filterA,
      filterD,
      onClick () {
        setFactoryStatusFilter([
          filterF.value ? 'F' : false,
          filterA.value ? 'A' : false,
          filterD.value ? 'D' : false,
        ].filter(Boolean) as ('D' | 'F' | 'A')[])
      }
    }
  }
})
</script>
