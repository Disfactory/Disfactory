<template>
  <div class="tutorial-modal-container">
    <app-modal :open="open" :dismiss="onDismissClick">
      <div class="page">
        <div id="tutorial-home" v-if="isHome">
          <h2>使用說明</h2>

          <p>
            如果系統無法讀取你的位置，
            請至手機系統設定開啟位置權限。
          </p>

          <div class="outline-button" @click="openAdd">如何新增一筆<br>違章工廠的資料？</div>
          <div class="outline-button" @click="openUpdate">如何在一筆資料裡<br>補充更多資訊？</div>
        </div>

        <div id="tutorial-add-factory" v-if="isAdd">

        </div>

        <div id="tutorial-update-factory" v-if="isUpdate">
          <carousel :per-page="1" paginationActiveColor='#6E8501' paginationColor='#e3e3e3' :paginationPadding="5">
          </carousel>
        </div>

      </div>
    </app-modal>
  </div>
</template>

<script lang="ts">
import AppModal from '@/components/AppModal.vue'
import { createComponent, ref, computed } from '@vue/composition-api'
import { Carousel, Slide } from 'vue-carousel'

export default createComponent({
  name: 'TutorialModal',
  components: {
    AppModal,
    Carousel,
    Slide
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
    const page = ref('home')

    const isHome = computed(() => page.value === 'home')
    const isAdd = computed(() => page.value === 'add')
    const isUpdate = computed(() => page.value === 'update')

    const openHome = () => page.value = 'home'
    const openAdd = () => page.value = 'add'
    const openUpdate = () => page.value = 'update'

    const onDismissClick = () => {
      switch (page.value) {
        case 'home':
          props.dismiss()
          break
        case 'add':
        case 'update':
          openHome()
          break
        default:
          props.dismiss()
          break
      }
    }

    return {
      isHome,
      isAdd,
      isUpdate,
      onDismissClick,
      openAdd,
      openUpdate
    }
  }
})
</script>

<style lang="scss">
@import '@/styles/page';
@import '@/styles/variables';

.tutorial-modal-container .app-modal {
  top: 20px;
  max-height: 100%;
  max-width: calc(100% - 20px);
  padding: 35px 45px;

  .page {
    height: auto;

    img {
      height: 200px;
      display: block;
      margin: 0 auto;

      @media (max-width: 480px) {
        height: 130px;
      }
    }

    h2 {
      color: $second-color;
      border: none;
    }

    #tutorial-home {
      p {
        font-weight: bold;
        margin-top: 2em;
        margin-bottom: 2em;
      }
    }
  }

  .outline-button {
    border: solid 1px $primary-color;
    padding: 10px 20px;
    color: $primary-color;
    margin-bottom: 15px;
    line-height: 1.5em;

    &:hover, &:active {
      color: white;
      background-color: $primary-color;
    }
  }
}
</style>
