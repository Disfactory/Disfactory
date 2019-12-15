<template>
  <div>
    <div class="navbar-container">
      <app-navbar :dark="false" :fixed="true" @back="onNavBack">
        {{ isCreateMode ? '新增資訊' : '補充資訊' }}
      </app-navbar>
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
        <h1>
          {{ isCreateMode ? '輸入資訊' : '輸入補充資訊' }}
        </h1>

        <h3>工廠地點</h3>
        <div class="minimap" ref="minimap" @click="onClickMinimap()" />

        <div class="flex justify-between" style="margin-top: 40px;">
          <div class="flex flex-column flex-auto">
            <h3 style="margin-top: 0;">工廠照片*</h3>
            <label>
              <small>請上傳至少一張照片</small>
            </label>
          </div>
          <div>
            <label>
              <input multiple type="file" accept="image/*" ref="image" @change="handleImagesUpload" style="visibility: hidden; position: absolute; pointer-events: none;">
              <app-button :disabled="!isCreateMode">新增</app-button>
            </label>
          </div>
        </div>

        <div class="images-grid">
          <div class="image-card" :key="url" v-for="url in imageUrls" >
            <img :src="url" />
          </div>
        </div>

        <h3>工廠名稱</h3>
        <div class="flex align-items-center">
          <div class="flex-auto">
            <app-text-field
              v-model="factoryName"
              placeholder="請輸入工廠名稱"
            />
          </div>

          <div style="width: 100px;" v-if="isEditMode">
            <app-button @click="updateFactoryFieldsFor('name', factoryName)">確認</app-button>
          </div>
        </div>

        <h3>工廠類型</h3>
        <div class="flex align-items-center">
          <div class="flex-auto">
            <app-select
              v-model="factoryType"
              :items="factoryTypeItems"
            />
          </div>

          <div style="width: 100px;" v-if="isEditMode">
            <app-button @click="updateFactoryFieldsFor('factory_type', factoryType)">確認</app-button>
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

          <div style="width: 100px;" v-if="isEditMode">
            <app-button @click="updateFactoryFieldsFor('others', factoryDescription)">確認</app-button>
          </div>
        </div>

        <div class="text-center width-auto" style="margin-top: 60px;" v-if="isCreateMode">
          <app-button @click="submitFactory()">送出</app-button>
        </div>

      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { createComponent, ref, computed, inject, Ref, onMounted, watch } from '@vue/composition-api'
import AppButton from '@/components/AppButton.vue'
import AppTextField from '@/components/AppTextField.vue'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSelect from '@/components/AppSelect.vue'
import ImageUploadModal from '@/components/ImageUploadModal.vue'
import { UploadedImages, createFactory, updateFactory } from '../api'
import { FactoryPostData, FACTORY_TYPE, FactoryType } from '../types'
import { MapFactoryController, initializeMinimap } from '../lib/map'
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
      defaultValue: 'create'
    },
    factoryData: {
      type: Object,
      required: true
    }
  },
  setup (props) {
    const mapController = inject(MainMapControllerSymbol, ref<MapFactoryController>())
    let minimapController: MapFactoryController

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
    const factoryDescription = ref('')
    let images: Ref<string[]>
    const nickname = ref('')
    const contact = ref('')

    // initialize factory values
    if (isCreateMode) {
      factoryName = ref(initialFactoryValue.factoryName)
      factoryType = ref(initialFactoryValue.factoryType)
      images = ref(initialFactoryValue.images)
    } else if (isEditMode) {
      const { factoryData } = props
      factoryName = ref(factoryData.name)
      factoryType = ref(factoryData.factory_type)
      images = ref(factoryData.images)
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

    const updateFactoryFieldsFor = async (field: string, value: string) => {
      const { factoryData } = props
      if (!isEditMode || !factoryData) {
        return
      }

      try {
        const factory = await updateFactory(factoryData.id, {
          [field]: value
        })

        if (mapController.value) {
          mapController.value.updateFactory(factoryData.id, factory)
        }
      } catch (err) {
        console.error(err)
      }
    }

    const minimap = ref<HTMLElement>(null)

    onMounted(() => {
      if (mapController.value) {
        const controller = mapController.value
        const center = controller.mapInstance.map.getView().getCenter() as number[]
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        minimapController = initializeMinimap(minimap.value!, center)
        minimapController.addFactories(controller.factories)

        if (isEditMode) {
          const { factoryData } = props
          minimapController.mapInstance.setMinimapPin(factoryData.lng, factoryData.lat)
        } else if (isCreateMode) {
          const [lng, lat] = props.factoryLocation as number[]
          minimapController.mapInstance.setMinimapPin(lng, lat)
        }
      }
    })

    watch(() => props.factoryLocation, () => {
      if (isCreateMode && minimapController) {
        const [lng, lat] = props.factoryLocation as number[]
        minimapController.mapInstance.setMinimapPin(lng, lat)
      }
    })

    return {
      minimap,
      onClickMinimap: () => {
        if (isCreateMode && mapController.value) {
          mapController.value.mapInstance.setLUILayerVisible(true)
          props.enterSelectFactoryMode()
        }
      },

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
        if (mapController.value) {
          mapController.value.mapInstance.setLUILayerVisible(false)
          props.close()
          props.exitSelectFactoryMode()
        }
      },
      async submitFactory () {
        try {
          const [lng, lat] = props.factoryLocation as number[]
          const factory: FactoryPostData = {
            name: factoryName.value,
            lng,
            lat,
            type: factoryType.value,
            others: factoryDescription.value,
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
        props.setCreateFactorySuccessModal(true)
      },
      finishUploaderForm,

      isEditMode,
      isCreateMode,
      updateFactoryFieldsFor
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

.page-container {
  overflow-x: hidden;
}

.navbar-container {
  position: absolute;
  top: -47px;
  left: 0;
  z-index: 2;
}

.minimap {
  cursor: pointer;
}
</style>
