<template>
  <div class="safety-modal-container">
    <app-modal :open="open" :dismiss="dismiss">
      <div class="page">
        <carousel :per-page="1" paginationActiveColor='#6E8501' paginationColor='#e3e3e3' :paginationPadding="5">
          <slide>
            <h1>安全須知</h1>
            <p>
              請參考以下建議，前往違章工廠拍照蒐證
            </p>
          </slide>
          <slide>
            <img src="/images/safety_notice/1.png" alt="">
            <h2>
              場勘
            </h2>
            <p>
              假裝路過，檢查有無監視器；尋找適合拍照的隱蔽處
            </p>
          </slide>
          <slide>
            <img src="/images/safety_notice/2.png" alt="">
            <h2>藏身</h2>
            <p>
              盡量避開監視器、他人視線；盡量在隱蔽處拍照（例如：車上、民宅內、樹叢間、遠方）
            </p>
          </slide>
          <slide>
            <img src="/images/safety_notice/3.png" alt="">
            <h2>避嫌</h2>
            <p>假如地點不夠隱密，請用手機拍照，降低他人戒心</p>
          </slide>
          <slide>
            <img src="/images/safety_notice/4.png" alt="">
            <h2>速離</h2>
            <p>拍到1張清晰照片即可離去</p>
          </slide>
          <slide>
            <img src="/images/safety_notice/5.png" alt="">
            <h2>應變</h2>
            <p>假如有人上前問話，請表現得「充滿好奇心」，試著跟對方聊天（例如：好奇水電師傅的施工技術），再伺機離開。</p>
          </slide>
        </carousel>
      </div>
    </app-modal>
  </div>
</template>

<script lang="ts">
import AppModal from '@/components/AppModal.vue'
import { createComponent } from '@vue/composition-api'
import { Carousel, Slide } from 'vue-carousel';

export default createComponent({
  name: 'SafetyModal',
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
  }
})
</script>

<style lang="scss">
@import '@/styles/page';
@import '@/styles/variables';

.safety-modal-container .app-modal {
  top: 20px;
  max-height: 100%;
  max-width: calc(100% - 20px);

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
      font-size: 44px;
      color: $primary-color;
      border: none;
      padding-bottom: 0;
      margin-bottom: -5px;
    }
  }
}
</style>
