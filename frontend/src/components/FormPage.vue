<template>
  <div>
    <div class="navbar-container">
      <app-navbar :dark="false" :fixed="true" @back="onNavBack">新增資訊</app-navbar>
    </div>

    <div class="page-container" :class="{ hide: selectFactoryMode }">
      <image-upload-modal
        :open="imageUploadModalOpen"
        :dismiss="closeImageUploadModal"
        :images="imagesToUpload"
        :finishImagesUpload="finishImagesUpload"
        :finishUploaderForm="finishUploaderForm"
      />

      <div class="page" style="padding: 29px 35px;">
        <h1>輸入資訊</h1>

        <h3>工廠地點</h3>
        {{ JSON.stringify(factoryLocation) }}

        <app-button v-if="isCreateMode" @click="enterSelectFactoryMode()">點我選擇</app-button>

        <div class="flex justify-between" style="margin-top: 40px;">
          <div class="flex flex-column flex-auto">
            <h3 style="margin-top: 0;">工廠照片*</h3>
            <label>
              <small>請上傳至少一張照片</small>
            </label>
          </div>
          <div>
            <label>
              <input multiple type="file" accept="image/*" ref="image" @change="handleImagesUpload" style="display: none;">
              <app-button :disabled="!isCreateMode" @click="image.click()">新增</app-button>
            </label>
          </div>
        </div>

        <div class="images-grid">
          <div class="image-card" :key="url" v-for="url in imageUrls" >
            <img :src="url" />
          </div>
        </div>

        <h3>工廠名稱</h3>
        <app-text-field
          v-model="factoryName"
          placeholder="請輸入工廠名稱"
        />

        <h3>工廠類型</h3>
        <div class="flex align-items-center">
          <div class="flex-auto">
            <app-select
              v-model="factoryType"
              :items="factoryTypeItems"
            />
          </div>

          <div style="width: 100px;">
            <app-button>確認</app-button>
          </div>
        </div>

        <h3>新增其它資訊</h3>
        <div class="flex align-items-center">
          <div class="flex-auto">
            <app-text-field
              v-model="factoryDescription"
              placeholder="請填入其他資訊，如聲音、氣味等等。"
            />
          </div>

          <div style="width: 100px;">
            <app-button>確認</app-button>
          </div>
        </div>

        <div class="text-center width-auto" style="margin-top: 60px; margin-bottom: 55px;" v-if="isCreateMode">
          <app-button @click="submitFactory()">送出</app-button>
        </div>

      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { createComponent, ref, computed, inject, Ref } from '@vue/composition-api'
import AppButton from '@/components/AppButton.vue'
import AppTextField from '@/components/AppTextField.vue'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSelect from '@/components/AppSelect.vue'
import ImageUploadModal from '@/components/ImageUploadModal.vue'
import { UploadedImages, createFactory } from '../api'
import { FactoryPostData, FACTORY_TYPE, FactoryType } from '../types'
import { MapFactoryController } from '../lib/map'
import { MainMapControllerSymbol } from '../symbols'

export default createComponent({
  name: 'FormPage',
  components: {
    AppButton,
    AppTextField,
    AppSelect,
    AppNavbar,
    ImageUploadModal
  },
  props: {
    // close form page
    close: {
      type: Function,
      required: true
    },
    selectFactoryMode: {
      type: Boolean,
      required: true
    },
    enterSelectFactoryMode: {
      type: Function,
      required: true
    },
    exitSelectFactoryMode: {
      type: Function,
      required: true
    },
    factoryLocation: {
      type: Array,
      required: true
    },
    setCreateFactorySuccessModal: {
      type: Function,
      required: true
    },
    mode: {
      type: String,
      required: true,
      defaultValue: 'create',
      validator: value => ['create', 'edit'].includes(value)
    },
    factoryData: {
      type: Object,
      required: false // should be given if when edit mode
    }
  },
  setup (props) {
    const mapController = inject(MainMapControllerSymbol, ref<MapFactoryController>())

    // mode helpers
    const isEditMode = props.mode === 'edit'
    const isCreateMode = props.mode === 'create'

    const factoryTypeItems: Array<{ text: string, value: string }> = [
      { text: '請選擇工廠類型', value: '0' },
      ...Object.entries(FACTORY_TYPE).map(([value, text]) => ({ text, value }))
    ]

    const initialFactoryValue = {
      factoryName: '',
      factoryType: '0',
      factoryDescription: '',
      images: [],
      lng: 0,
      lat: 0,
      nickname: '',
      other: '',
      contact: ''
    }
    let factoryName: Ref<string>
    let factoryType: Ref<FactoryType>
    let factoryDescription: Ref<string>
    let images: Ref<string[]>
    let nickname: Ref<string>
    let other: Ref<string>
    let contact: Ref<string>

    // initialize factory values
    if (isCreateMode) {
      factoryName = ref(initialFactoryValue.factoryName)
      factoryType = ref(initialFactoryValue.factoryType)
      factoryDescription = ref(initialFactoryValue.factoryDescription)
      images = ref(initialFactoryValue.images)
      nickname = ref(initialFactoryValue.nickname)
      other = ref(initialFactoryValue.other)
      contact = ref(initialFactoryValue.contact)
    } else if (isEditMode) {
      const { factoryData } = props

      factoryName = ref(factoryData.factoryName)
      factoryType = ref(factoryData.factoryType)
      factoryDescription = ref(factoryData.factoryDescription)
      images = ref(factoryData.images)
      nickname = ref(factoryData.nickname)
      other = ref(factoryData.other)
      contact = ref(factoryData.contact)
    } else {
      throw new TypeError('Invalid mode!')
    }

    const imageUploadModalOpen = ref(false)
    const closeImageUploadModal = () => {
      imageUploadModalOpen.value = false
    }
    const openImageUploadModal = () => {
      imageUploadModalOpen.value = true
    }

    const imagesToUpload = ref<FileList>([])
    const uploadedImages = ref<UploadedImages>([])
    const image = ref<HTMLElement>(null)

    const imageUrls = computed(() => {
      const urls = []
      for (let i = 0; i < imagesToUpload.value.length; i++) {
        urls.push(URL.createObjectURL(imagesToUpload.value[i]))
      }

      return urls
    })

    const finishUploaderForm = (_nickname: string, _contact: string) => {
      nickname.value = _nickname
      contact.value = _contact
    }

    return {
      factoryName,
      factoryType,
      factoryTypeItems,
      factoryDescription,
      containerStyle: {
        width: '100%'
      },
      imageUploadModalOpen,
      openImageUploadModal,
      closeImageUploadModal,

      imageUrls,
      imagesToUpload,
      image, // image upload input ref,
      handleImagesUpload (e: Event) {
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        imagesToUpload.value = (e.target as HTMLInputElement).files!

        openImageUploadModal()
      },
      finishImagesUpload (_images: UploadedImages) {
        uploadedImages.value = _images
        images.value = _images.map(image => image.token)
      },
      onNavBack () {
        props.close()
        props.exitSelectFactoryMode()
      },
      async submitFactory () {
        try {
          const [lng, lat] = props.factoryLocation as number[]
          const factory: FactoryPostData = {
            name: factoryName.value,
            lng,
            lat,
            type: factoryType.value,
            other: factoryDescription.value,
            images: uploadedImages.value.map(image => image.token),
            nickname: nickname.value,
            contact: contact.value
          }

          const resultFactory = await createFactory(factory)
          if (mapController.value) {
            mapController.value.addFactories([resultFactory])
          }
        } catch (e) {
          // TODO: handle create failure
        }

        // TODO: clear form

        props.close()
        props.exitSelectFactoryMode()
        console.log(props.setCreateFactorySuccessModal)
        props.setCreateFactorySuccessModal(true)
      },
      finishUploaderForm,

      isEditMode,
      isCreateMode
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/styles/utils';
@import '@/styles/page';
@import '@/styles/images-grid';

.page-container.hide {
  display: none;

  .navbar-container {
    display: block;
  }
}

.navbar-container {
  position: absolute;
  top: -47px;
  left: 0;
  z-index: 2;
}
</style>
