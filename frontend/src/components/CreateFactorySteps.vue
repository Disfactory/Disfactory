<template>
  <div class="create-factory-steps" v-if="appState.isCreateMode">
    <v-app-bar
      fixed
      color="white"
    >
      <div class="btn-container" :class="{ hide: appState.createStepIndex === 1 }">
        <v-btn icon @click="onBack">
          <v-icon>mdi-keyboard-backspace</v-icon>
        </v-btn>
      </div>

      <v-spacer></v-spacer>
      <v-toolbar-title>新增可疑工廠 步驟 ({{ appState.createStepIndex }}/3)</v-toolbar-title>
      <v-spacer></v-spacer>

      <div class="btn-container">
        <v-btn icon @click="cancelCreateFactory">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>

    </v-app-bar>


    <div class="create-factory-step-1" v-if="appState.createStepIndex === 1">
      <v-btn rounded color="white" class="mr-2">
        顯示經緯度
      </v-btn>

      <v-btn rounded color="white">
        切換地圖模式•簡易地圖
      </v-btn>

      <v-container fluid class="choose-location-btn-container d-flex justify-center" bottom="50">
        <v-btn x-large rounded @click="chooseLocation">
          選擇此地點
        </v-btn>
      </v-container>
    </div>

    <image-upload-form
      v-if="appState.createStepIndex === 2"
      v-model="selectedImages"
      :uploading="imageUploadState.uploading"
      :error="imageUploadState.error"
      :previewImages="uploadedImages"
      :onClickRemoveImage="onClickRemoveImage"
      :valid="imageUploadFormValid"
      :submit="pageTransition.gotoNextCreate"
      :formState="formState"
    />

    <confirm-factory
      v-if="appState.createStepIndex === 3"
      :formState="formState"
      :previewImages="uploadedImages"
    />

  </div>
</template>

<script lang="ts">
import { createComponent, inject, ref, watch, reactive, computed } from '@vue/composition-api'

import { useAppState } from '../lib/appState'
import { useAlertState } from '../lib/useAlert'

import { MainMapControllerSymbol } from '../symbols'
import { MapFactoryController } from '../lib/map'
import { uploadImages, UploadedImage } from '../api'

import ImageUploadForm from './ImageUploadForm.vue'
import ConfirmFactory from './ConfirmFactory.vue'

export default createComponent({
  name: 'CreateFactorySteps',
  components: {
    ImageUploadForm,
    ConfirmFactory
  },
  setup (props) {
    const [appState, { pageTransition, setFactoryLocation }] = useAppState()
    const [, alertActions] = useAlertState()

    const mapController = inject(MainMapControllerSymbol, ref<MapFactoryController>())

    function cancelCreateFactory () {
      if (mapController.value) {
        mapController.value.mapInstance.setLUILayerVisible(false)
        pageTransition.closeFactoryPage()
      }
    }

    const onBack = () => {
      if (appState.createStepIndex === 1) {
        cancelCreateFactory()
      } else if (appState.createStepIndex === 2) {
        if (mapController.value) {
          mapController.value.mapInstance.setLUILayerVisible(true)
          pageTransition.previousCreateStep()
        }
      } else {
        pageTransition.previousCreateStep()
      }
    }

    const createFactoryFormState = reactive({
      nickname: '',
      contact: ''
    })

    const uploadedImages = ref<UploadedImage[]>([])
    const imageUploadState = reactive({
      error: null,
      uploading: false
    })

    const selectedImages = ref<FileList>(null)
    watch(selectedImages, async () => {
      if (!selectedImages.value) {
        return
      }

      imageUploadState.uploading = true

      // TODO: handle image upload error
      const images = await uploadImages(selectedImages.value)

      uploadedImages.value = [
        ...uploadedImages.value,
        ...images
      ]

      imageUploadState.uploading = false
    })

    const onClickRemoveImage = ({ src } : UploadedImage) => {
      uploadedImages.value = uploadedImages.value.filter(image => image.src !== src)
    }

    const imageUploadFormValid = computed(() => uploadedImages.value.length > 0)

    return {
      appState,
      pageTransition,
      formState: createFactoryFormState,

      cancelCreateFactory,
      onBack,
      chooseLocation () {
        if (!mapController.value) return

        if (!appState.canPlaceFactory) {
          alertActions.showAlert('此地點不在農地範圍內，\n請回報在農地範圍內的工廠。')
          return
        }

        mapController.value.mapInstance.setLUILayerVisible(false)

        setFactoryLocation(appState.mapLngLat as [number, number])

        pageTransition.nextCreateStep()
      },
      selectedImages,
      imageUploadState,
      uploadedImages,
      onClickRemoveImage,
      imageUploadFormValid
    }
  }
})
</script>

<style lang="scss" scoped>
.btn-container.hide {
  visibility: hidden;
  pointer-events: none;
}

.create-factory-steps {
  .create-factory-step-1 {
    padding: 20px 15px;

    .choose-location-btn-container {
      position: fixed;
      bottom: 50px;
    }
  }
}
</style>
