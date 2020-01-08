<template>
  <div class="filter-modal-container">
    <app-modal :open="open" :dismiss="dismiss">
      <div class="page">
        <div class="page-inner">
          <h2 style="margin-right: 30px;">篩選</h2>
          <label class="checkbox-container" v-for="status in FACTORY_STATUS_ITEMS" :key="status">
            <input type="checkbox" :name="status" v-model="filters[status]">
            <span class="checkbox" />
            <span class="data-type" :class="{ 'has-description': FactoryStatusText[status][1] }">
              {{ FactoryStatusText[status][0] }}
              <small v-if="FactoryStatusText[status][1]">{{ FactoryStatusText[status][1] }}</small>
            </span>
            <span class="space" />
            <img :src="`/images/marker-${status}.svg`">
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
import { FactoryStatusText, FactoryStatus, FACTORY_STATUS_ITEMS } from '../types'

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
      [FactoryStatus.NEW]: false,
      [FactoryStatus.EXISTING_INCOMPLETE]: false,
      [FactoryStatus.EXISTING_COMPLETE]: false,
      [FactoryStatus.REPORTED]: false
    })

    const mapController = inject(MainMapControllerSymbol, ref<MapFactoryController>())

    return {
      filters,
      onClick () {
        if (!mapController.value) {
          return
        }

        const statusTypes = Object.entries(filters)
          .map(([key, value]) => value ? key : false)
          .filter(Boolean) as FactoryStatus[]

        mapController.value.setFactoryStatusFilter(statusTypes)

        if (typeof props.dismiss === 'function') {
          props.dismiss()
        }
      },
      FACTORY_STATUS_ITEMS,
      FactoryStatus,
      FactoryStatusText
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

  .checkbox-container {
    position: relative;
  }

  .data-type {
    min-width: 80px;

    &.has-description {
      small {
        position: absolute;
        margin-bottom: 20px;
        left: 31px;
        top: 25px;
        font-size: 12px;
      }
    }
  }

  .app-modal {
    top: 50px;
  }
}

</style>
