<template>
  <div class="filter-modal-container">
    <app-modal :open="open" :dismiss="dismiss">
      <div class="page">
        <div class="page-inner">
          <h2 style="margin-right: 30px;">篩選</h2>
          <label class="checkbox-container" v-for="factoryStatus in FACTORY_STATUS_ITEMS" :key="factoryStatus">
            <input type="checkbox" :name="factoryStatus" v-model="filters[factoryStatus]">
            <span class="checkbox" />
            <span class="data-type">{{ FACTORY_STATUS[factoryStatus] }}</span>
            <span class="line" />
            <img :src="`/images/marker-${factoryStatus}.svg`">
          </label>
        </div>
        <div style="margin-bottom: 10px;">
          <app-button @click="onClick()">確認</app-button>
        </div>
      </div>
    </app-modal>
  </div>
</template>

<script lang="ts">
import AppModal from '@/components/AppModal.vue'
import AppButton from '@/components/AppButton.vue'
import { MapFactoryController } from '../lib/map'
import { createComponent, ref, inject, reactive } from '@vue/composition-api'
import { MainMapControllerSymbol } from '../symbols'
import { FactoryStatusType, FACTORY_STATUS, FACTORY_STATUS_ITEMS } from '../types'

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
  setup (props) {
    const filters = reactive({
      C: false,
      CO: false,
      CN: false,
      IO: false,
      IN: false
    }) as { [key in FactoryStatusType]: boolean }

    const mapController = inject(MainMapControllerSymbol, ref<MapFactoryController>())

    return {
      filters,
      onClick () {
        if (!mapController.value) {
          return
        }

        const statusTypes = Object.entries(filters)
          .map(([key, value]) => value ? key : false)
          .filter(Boolean) as FactoryStatusType[]

        mapController.value.setFactoryStatusFilter(statusTypes)

        if (typeof props.dismiss === 'function') {
          props.dismiss()
        }
      },
      FACTORY_STATUS_ITEMS,
      FACTORY_STATUS
    }
  }
})
</script>

<style lang="scss">
@import '@/styles/page';

.filter-modal-container {
  .page-inner {
    margin-bottom: 20px;
    padding: 0 10px;
  }

  .data-type {
    min-width: 80px;
  }

  .app-modal {
    top: 50px;
  }
}

</style>
