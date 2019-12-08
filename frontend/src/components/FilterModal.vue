<template>
  <app-modal :open="open" :dismiss="dismiss">
    <div class="page">
      <div class="page-inner">
        <h2 style="margin-right: 30px;">篩選</h2>
        <label class="checkbox-container">
          <input type="checkbox" name="F" v-model="filterF">
          <span class="checkbox" />
          資料不全
          <span class="line" />
          <img src="/images/marker-red.svg">
        </label>
        <label class="checkbox-container">
          <input type="checkbox" name="A" v-model="filterA">
          <span class="checkbox" />
          資料齊全
          <span class="line" />
          <img src="/images/marker-blue.svg">
        </label>
        <label class="checkbox-container">
          <input type="checkbox" name="D" v-model="filterD">
          <span class="checkbox" />
          已舉報
          <span class="line" />
          <img src="/images/marker-green.svg">
        </label>
      </div>
      <app-button @click="onClick()">確認</app-button>
    </div>
  </app-modal>
</template>

<script lang="ts">
import AppModal from '@/components/AppModal.vue'
import AppButton from '@/components/AppButton.vue'
import { MapFactoryController } from '../lib/map'
import { createComponent, reactive, ref, inject } from '@vue/composition-api'
import { MainMapControllerSymbol } from '../symbols'

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
    },
    dismiss: {
      type: Function
    }
  },
  setup (props, context) {
    const filterF = ref(false)
    const filterA = ref(false)
    const filterD = ref(false)

    const mapController = inject(MainMapControllerSymbol, ref<MapFactoryController>())

    return {
      filterF,
      filterA,
      filterD,
      onClick () {
        mapController.value!.setFactoryStatusFilter([
          filterF.value ? 'F' : false,
          filterA.value ? 'A' : false,
          filterD.value ? 'D' : false
        ].filter(Boolean) as ('D' | 'F' | 'A')[])

        if (typeof props.dismiss === 'function') {
          props.dismiss()
        }
      }
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/styles/page';

.page-inner {
  margin-bottom: 20px;
  padding: 0 10px;
}
</style>
