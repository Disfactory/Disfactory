<template>
  <div>
    <div class="navbar-container">
      <app-navbar :dark="false" :fixed="true" @back="onNavBack" @menu="modalActions.toggleSidebar">
        {{ isCreateMode ? '新增資訊' : '補充資訊' }}
      </app-navbar>
    </div>

    <div class="page-container" :class="{ hide: selectFactoryMode }">
      <image-upload-modal
        :open="formPageState.imageUploadModalOpen"
        :dismiss="closeImageUploadModal"
        :images="imagesToUpload"
        :finishImagesUpload="finishImagesUpload"
        :finishUploaderForm="finishUploaderForm"
        :mode="mode"
        :factoryData="factoryData"
      />

      <div class="page" style="padding: 29px 35px;">
        <div class="status-banner flex" v-if="!isCreateMode" :style="{ backgroundColor: getStatusBorderColor(factoryFormState.status) }">
          <img src="/images/marker-white.svg" style="margin-right: 7px;">
          {{ FactoryStatusText[factoryFormState.status][0] }}
        </div>

        <h2>
          上傳工廠資訊

          <small v-if="isCreateMode">
            <br><br>
            請確認工廠地點，
            <br>
            並上傳至少一張照片。
          </small>

          <small v-else>
            <br>
            請上傳至少一張照片。
          </small>
        </h2>

        <div class="minimap" ref="minimap" @click="onClickMinimap()" data-label="form-minimap" />

        <div class="flex justify-between" style="margin-top: 40px; margin-bottom: 20px;">
          <div>
            <h3 style="margin-top: 0;">工廠照片*</h3>

            <div style="width: 100px; margin-bottom: 15px;">
              <label data-label="form-add-image">
                <input multiple type="file" accept="image/*" ref="image" style="visibility: hidden; position: absolute; left: -1000px;"  data-label="form-add-image" @change="handleImagesUpload">
                <app-button rect @click="onClickImageUpload" data-label="form-add-image">新增</app-button>
              </label>
            </div>

            <div>
              <small>若您的 iPhone 手機的系統為 iOS 13.3 以下（包含），可能無法上傳照片，工程師搶修中，敬請見諒 🥺</small>
            </div>
          </div>

        </div>

        <div class="images-grid">
          <div class="image-card" :key="url" v-for="url in factoryFormState.imageUrls" >
            <img :src="url" />
          </div>
        </div>

        <h2>
          補充其他資訊
          <small>
            <br>
            若無可跳過
          </small>
        </h2>

        <h3>工廠描述</h3>
        <div class="flex align-items-center">
          <div class="flex-auto">
            <app-text-area
              v-model="factoryFormState.others"
              :placeholder="'說明為何工廠可疑，\n如聲音類型、氣味類型等等。'"
            />
          </div>

          <div style="width: 100px; height: 47px; margin-left: -3px;" v-if="isEditMode">
            <app-button @click="updateFactoryFieldsFor('others', factoryFormState.others)" rect :disabled="fieldSubmittingState.others_submitting" data-label="form-update-others">
              {{ fieldSubmittingState.others_submitting ? '更新中' : '更新' }}
            </app-button>
          </div>
        </div>

        <h3>工廠外部文字</h3>
        <div class="flex align-items-center">
          <div class="flex-auto">
            <app-text-field
              v-model="factoryFormState.name"
              placeholder="輸入可幫助辨識工廠的文字"
            />
          </div>

          <div style="width: 100px; height: 47px; margin-left: -3px;" v-if="isEditMode">
            <app-button @click="updateFactoryFieldsFor('name', factoryFormState.name)" rect :disabled="fieldSubmittingState.name_submitting" data-label="form-update-name">
              {{ fieldSubmittingState.name_submitting ? '更新中' : '更新' }}
            </app-button>
          </div>
        </div>

        <h3>工廠類型</h3>
        <div class="flex align-items-center">
          <div class="flex-auto">
            <app-select
              v-model="factoryFormState.type"
              :items="factoryTypeItems"
            />
          </div>

          <div style="width: 100px; height: 47px; margin-left: -3px;" v-if="isEditMode">
            <app-button @click="updateFactoryFieldsFor('factory_type', factoryFormState.type)" rect :disabled="fieldSubmittingState.factory_type_submitting" data-label="form-update-factoryType">
              {{ fieldSubmittingState.factory_type_submitting ? '更新中' : '更新' }}
            </app-button>
          </div>
        </div>

        <div class="text-center width-auto" style="margin-top: 60px;" v-if="isCreateMode">
          <app-button @click="submitFactory()" :disabled="formPageState.submitting"  data-label="form-create-submit">
            {{ formPageState.submitting ? '上傳資料中' : '送出' }}
          </app-button>
        </div>

      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { createComponent, ref, inject, onMounted, watch, reactive } from '@vue/composition-api'
import AppButton from '@/components/AppButton.vue'
import AppTextField from '@/components/AppTextField.vue'
import AppTextArea from '@/components/AppTextArea.vue'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSelect from '@/components/AppSelect.vue'
import ImageUploadModal from '@/components/ImageUploadModal.vue'
import { UploadedImages, createFactory, updateFactory } from '../api'
import {
  FactoryPostData,
  FACTORY_TYPE,
  FactoryType,
  FactoryData,
  FactoryImage,
  FactoryStatusText
} from '../types'
import { MapFactoryController, initializeMinimap, getStatusBorderColor, getFactoryStatus } from '../lib/map'
import { MainMapControllerSymbol } from '../symbols'
import { useBackPressed } from '../lib/useBackPressed'
import { useGA } from '@/lib/useGA'
import { useModalState } from '../lib/hooks'
import { useAppState } from '../lib/appState'
import { useAlertState } from '../lib/useAlert'

export default createComponent({
  name: 'FormPage',
  components: {
    AppButton,
    AppTextField,
    AppTextArea,
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
    const { event } = useGA()
    const mapController = inject(MainMapControllerSymbol, ref<MapFactoryController>())
    let minimapController: MapFactoryController
    const [, modalActions] = useModalState()
    const [appState] = useAppState()
    const [, alertActions] = useAlertState()

    const onBack = () => {
      if (mapController.value) {
        mapController.value.mapInstance.setLUILayerVisible(false)
        props.close()
        props.exitSelectFactoryMode()
      }
    }

    useBackPressed(onBack)

    // mode helpers
    const isEditMode = props.mode === 'edit'
    const isCreateMode = props.mode === 'create'

    const factoryTypeItems: Array<{ text: string, value: string }> = [
      { text: '請選擇工廠類型', value: '0' },
      ...FACTORY_TYPE
    ]

    const initialFactoryState = {
      name: '',
      others: '', // description
      type: '0' as FactoryType | '0',
      lng: 0,
      lat: 0,

      // image upload data
      images: [] as string[],
      imageUrls: [] as string[],
      nickname: '',
      contact: '',
      status: ''
    }

    // merge state
    if (isEditMode) {
      const { factoryData } = props

      initialFactoryState.name = factoryData.name
      initialFactoryState.type = factoryData.factory_type
      initialFactoryState.others = factoryData.others
      initialFactoryState.imageUrls = (factoryData.images as FactoryImage[]).map(image => image.image_path)
      initialFactoryState.lng = factoryData.lng
      initialFactoryState.lat = factoryData.lat
      initialFactoryState.status = getFactoryStatus(factoryData as FactoryData)
    }

    const factoryFormState = reactive(initialFactoryState)

    const formPageState = reactive({
      imageUploadModalOpen: false,
      valid: false,
      submitting: false
    })

    const fieldSubmittingState = reactive({
      // eslint-disable-next-line @typescript-eslint/camelcase
      name_submitting: false,
      // eslint-disable-next-line @typescript-eslint/camelcase
      factory_type_submitting: false,
      // eslint-disable-next-line @typescript-eslint/camelcase
      others_submitting: false
    })

    watch(() => {
      const {
        images
      } = factoryFormState
      const imagesValid = images.length > 0

      formPageState.valid = imagesValid
    })

    const closeImageUploadModal = () => {
      formPageState.imageUploadModalOpen = false
      event('closeImageUploadModal')
    }
    const openImageUploadModal = () => {
      formPageState.imageUploadModalOpen = true
      event('openImageUploadModal')
    }

    const imagesToUpload = ref<FileList>([])
    const image = ref<HTMLElement>(null)

    const finishUploaderForm = (nickname: string, contact: string) => {
      factoryFormState.nickname = nickname
      factoryFormState.contact = contact
    }

    const updateFactoryFieldsFor = async (field: string, value: string) => {
      const { factoryData } = props
      if (!isEditMode || !factoryData) {
        return
      }

      const updateKey = `${field}_submitting` as keyof typeof fieldSubmittingState

      try {
        fieldSubmittingState[updateKey] = true

        event('updateFactory', { field })
        const factory = await updateFactory(factoryData.id, {
          [field]: value
        })

        fieldSubmittingState[updateKey] = false

        if (mapController.value) {
          mapController.value.updateFactory(factoryData.id, factory)
          appState.factoryData = factory
        }
        modalActions.openUpdateFactorySuccessModal()
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
      factoryFormState,
      formPageState,
      fieldSubmittingState,
      factoryTypeItems,
      containerStyle: {
        width: '100%'
      },
      openImageUploadModal,
      closeImageUploadModal,

      imagesToUpload,
      image, // image upload input ref,
      onClickImageUpload () {
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        image.value!.click()
      },
      handleImagesUpload (e: Event) {
        // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
        imagesToUpload.value = (e.target as HTMLInputElement).files!

        openImageUploadModal()
      },
      async finishImagesUpload (_images: UploadedImages | FactoryImage[], imageUrls: string[]) {
        if (isCreateMode) {
          factoryFormState.imageUrls = imageUrls
          factoryFormState.images = (_images as UploadedImages).map(image => image.token)
        } else if (isEditMode) {
          // TODO: refactor into sepearte method...
          try {
            const factory = { ...props.factoryData } as FactoryData
            const images = _images as FactoryImage[]

            factoryFormState.imageUrls = factoryFormState.imageUrls.concat(imageUrls)

            factory.images = factory.images.concat(images)

            if (mapController.value) {
              mapController.value.updateFactory(props.factoryData.id, factory)
              appState.factoryData = factory
            }
            modalActions.openUpdateFactorySuccessModal()
          } catch (err) {
            console.error(err)
          }
        }
      },
      onNavBack () {
        if (mapController.value) {
          onBack()
        }
      },
      async submitFactory () {
        if (!formPageState.valid) {
          alertActions.showAlert('您沒上傳工廠照片，\n請上傳至少一張照片以完成回報。')
          return
        }

        formPageState.submitting = true

        try {
          const [lng, lat] = props.factoryLocation as number[]
          const factory: FactoryPostData = {
            name: factoryFormState.name,
            others: factoryFormState.others,
            type: factoryFormState.type as FactoryType,
            lng,
            lat,
            images: factoryFormState.images,
            nickname: factoryFormState.nickname,
            contact: factoryFormState.contact
          }

          event('createFactory', { lng, lat })
          const resultFactory = await createFactory(factory)
          if (mapController.value) {
            mapController.value.addFactories([resultFactory])
          }
        } catch (e) {
          // TODO: handle create failure
        } finally {
          formPageState.submitting = false
        }

        // TODO: clear form

        props.close()
        props.exitSelectFactoryMode()
        props.setCreateFactorySuccessModal(true)
      },
      finishUploaderForm,

      isEditMode,
      isCreateMode,
      updateFactoryFieldsFor,

      getStatusBorderColor,
      FactoryStatusText,
      getFactoryStatus,
      modalActions
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

.page {
  .status-banner {
    left: 0;
    top: 0;
    color: white;
    padding: 15px 35px;
    width: calc(100% + 70px);
    margin-left: -35px;
    margin-top: -28px;
  }

  h2 small {
    font-size: 14px;
    font-weight: normal;
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

  @media (min-width: 767.99999px) {
    display: block;
    margin: 0 auto;
    max-width: 500px;
    max-height: 400px;
  }
}
</style>
