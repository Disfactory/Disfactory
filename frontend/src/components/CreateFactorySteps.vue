<template>
  <div class="create-factory-steps">
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
        <v-dialog v-model="discardDialog" max-width="290">
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon v-on="on" v-bind="attrs">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </template>
          <v-card>
            <v-card-title class="headline">放棄新增可疑工廠嗎？</v-card-title>
            <v-card-text>放棄新增可疑工廠時，你將遺失所有已輸入的資料。下次需重新填寫。</v-card-text>
            <v-container class="text-center">
              <v-btn width="100%" x-large rounded color="green darken-1" @click="cancelCreateFactory">放棄新增</v-btn>
              <a class="d-block mt-4" @click="discardDialog = false">繼續填寫資料</a>
            </v-container>
          </v-card>
        </v-dialog>
      </div>

    </v-app-bar>


    <div class="create-factory-step-1" v-if="appState.createStepIndex === 1">
      <v-btn rounded color="white" class="mr-2">
        顯示經緯度
      </v-btn>

      <v-bottom-sheet v-model="mapModeBottomSheet">
        <template v-slot:activator="{ on, attrs }">
          <v-btn
            rounded
            color="white"
            v-bind="attrs"
            v-on="on"
          >
            切換地圖模式•簡易地圖
          </v-btn>
        </template>
        <v-list>
          <v-subheader>切換地圖模式</v-subheader>
          <v-list-item
            v-for="mode in mapModes"
            :key="mode.type"
            @click="clickChangeBaseLayer(mode)"
          >
            <v-list-item-title>{{ mode.name }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-bottom-sheet>

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
      :submit="submitFactory"
    />

  </div>
</template>

<script lang="ts">
import { createComponent, inject, ref, watch, reactive, computed } from '@vue/composition-api'

import { useAppState } from '../lib/appState'
import { useAlertState } from '../lib/useAlert'

import { MainMapControllerSymbol } from '../symbols'
import { MapFactoryController, BASE_MAP_NAME, BASE_MAP } from '../lib/map'
import { uploadImages, UploadedImage, createFactory } from '../api'

import ImageUploadForm from './ImageUploadForm.vue'
import ConfirmFactory from './ConfirmFactory.vue'
import { FactoryPostData, FactoryType } from '../types'
import { useGA } from '../lib/useGA'
import { useBackPressed } from '../lib/useBackPressed'

export default createComponent({
  name: 'CreateFactorySteps',
  components: {
    ImageUploadForm,
    ConfirmFactory
  },
  setup (props) {
    const [appState, { pageTransition, setFactoryLocation }] = useAppState()
    const [, alertActions] = useAlertState()
    const { event } = useGA()

    const discardDialog = ref(false)

    const mapController = inject(MainMapControllerSymbol, ref<MapFactoryController>())

    function cancelCreateFactory () {
      if (mapController.value) {
        mapController.value.mapInstance.setLUILayerVisible(false)
        discardDialog.value = false
        // TODO: clear form value
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
    useBackPressed(onBack)

    const mapModes = [BASE_MAP.SATELITE, BASE_MAP.OSM, BASE_MAP.TAIWAN].map(type => ({
      type,
      name: BASE_MAP_NAME[type]
    }))
    const clickChangeBaseLayer = (mode: { type: BASE_MAP, name: string }) => {
      if (mapController.value) {
        mapController.value?.mapInstance.changeBaseMap(mode.type)

        mapModeBottomSheet.value = false
      }
    }
    const mapModeBottomSheet = ref(false)

    const createFactoryFormState = reactive({
      nickname: '',
      contact: '',
      others: '',
      name: '',
      type: '0',
      submitting: false
    })

    const uploadedImages = ref<UploadedImage[]>([])
    const imageUploadState = reactive({
      error: null as boolean | null,
      uploading: false
    })

    const selectedImages = ref<FileList>(null)
    watch(selectedImages, async () => {
      imageUploadState.error = null

      if (!selectedImages.value) {
        return
      }

      imageUploadState.uploading = true

      try {
        const images = await uploadImages(selectedImages.value)

        uploadedImages.value = [
          ...uploadedImages.value,
          ...images
        ]
      } catch (err) {
        console.error(err)
        imageUploadState.error = true
      }

      imageUploadState.uploading = false
    })

    const onClickRemoveImage = ({ src } : UploadedImage) => {
      uploadedImages.value = uploadedImages.value.filter(image => image.src !== src)
    }

    const imageUploadFormValid = computed(() => uploadedImages.value.length > 0 && !imageUploadState.uploading)

    const submitFactory = async () => {
      createFactoryFormState.submitting = true

      try {
        const [lng, lat] = appState.factoryLocation as number[]
        const factory: FactoryPostData = {
          name: createFactoryFormState.name,
          others: createFactoryFormState.others,
          type: createFactoryFormState.type as FactoryType,
          lng,
          lat,
          images: uploadedImages.value.map(i => i.token),
          nickname: createFactoryFormState.nickname,
          contact: createFactoryFormState.contact
        }

        event('createFactory', { lng, lat })
        const resultFactory = await createFactory(factory)
        if (mapController.value) {
          mapController.value.addFactories([resultFactory])
        }
      } catch (e) {
        // TODO: handle create failure
      } finally {
        createFactoryFormState.submitting = false
      }

      // TODO: if error, don't close factory page
      pageTransition.closeFactoryPage()
    }

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
      imageUploadFormValid,
      discardDialog,
      submitFactory,
      mapModes,
      clickChangeBaseLayer,
      mapModeBottomSheet
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
