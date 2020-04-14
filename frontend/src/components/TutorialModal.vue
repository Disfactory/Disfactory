<template>
  <div class="tutorial-modal-container">
    <app-modal :open="open" :dismiss="onDismissClick">
      <div class="back-button" v-if="isAdd || isUpdate" @click="openHome">
        <span />
        <span />
        <span />
      </div>

      <div class="page">
        <div id="tutorial-home" v-show="isHome">
          <h2>使用說明</h2>

          <p>
            如果系統無法讀取你的位置，
            請至手機系統設定開啟位置權限。
          </p>

          <div class="outline-button" @click="openAdd">如何新增一筆<br>違章工廠的資料？</div>
          <div class="outline-button" @click="openUpdate">如何在一筆資料裡<br>補充更多資訊？</div>
        </div>

        <div id="tutorial-add-factory" v-show="isAdd">

          <carousel :per-page="1" paginationActiveColor='#6E8501' paginationColor='#e3e3e3' :paginationPadding="5" ref="createCarousel">
            <slide v-for="(image, index) in addImages" :key="image">
              <h2>新增違章工廠({{index + 1}}/5)</h2>
              <img :src="image">
            </slide>
          </carousel>
        </div>

        <div id="tutorial-update-factory" v-show="isUpdate">
          <carousel :per-page="1" paginationActiveColor='#6E8501' paginationColor='#e3e3e3' :paginationPadding="5" ref="updateCarousel">
            <slide v-for="(image, index) in updateImages" :key="image">
              <h2>補充工廠資訊({{index + 1}}/2)</h2>
              <img :src="image">
            </slide>
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

    const createCarousel = ref<HTMLElement>(null)
    const updateCarousel = ref<HTMLElement>(null)

    const openHome = () => { page.value = 'home' }
    const openAdd = () => {
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion, @typescript-eslint/no-explicit-any
      (createCarousel.value! as any).goToPage(0)
      page.value = 'add'
    }
    const openUpdate = () => {
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion, @typescript-eslint/no-explicit-any
      (updateCarousel.value! as any).goToPage(0)
      page.value = 'update'
    }

    const addImages = new Array(5).fill(true).map((_, index) => `/images/tutorial/new_${index + 1}.png`)
    const updateImages = new Array(2).fill(true).map((_, index) => `/images/tutorial/update_${index + 1}.png`)

    const onDismissClick = () => {
      openHome()
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      props.dismiss!()
    }

    return {
      isHome,
      isAdd,
      isUpdate,
      openHome,
      openAdd,
      openUpdate,
      addImages,
      updateImages,
      onDismissClick,
      createCarousel,
      updateCarousel
    }
  }
})
</script>

<style lang="scss">
@import '@/styles/page';
@import '@/styles/variables';
@import '@/styles/components/back-button';

.tutorial-modal-container .app-modal {
  top: 20px;
  max-height: 100%;
  max-width: calc(100% - 20px);
  padding: 70px 45px 35px;

  .page {
    height: auto;

    img {
      display: block;
      margin: 0 auto;
      max-height: 65vh;
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

    #tutorial-add-factory, #tutorial-update-factory {
      h2 {
        margin-right: 0;
        text-align: center;
        color: $primary-color;
      }
    }
  }

  .outline-button {
    border: solid 1px $primary-color;
    padding: 10px 20px;
    color: $primary-color;
    margin-bottom: 15px;
    line-height: 1.5em;
    user-select: none;
    cursor: pointer;

    &:hover, &:active {
      color: white;
      background-color: $primary-color;
    }
  }

  .back-button {
    position: absolute;
    top: 24px;
    left: 22px;
  }
}
</style>
