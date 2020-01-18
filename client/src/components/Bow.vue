<template>
    <div class="container-fluid">
        <div v-if="showLoading"
             class="loading-overlay d-flex align-items-center justify-content-center">
            <BSpinner label="Loading..." style="width: 6rem; height: 6rem;"></BSpinner>
        </div>
        <b-alert v-model="error" variant="warning" dismissible>
            {{errorMessage}}
        </b-alert>
        <div class="row">
            <div class="col-6">
                <div class="container-fluid">
                    <div class="row">
                        <div class="col-12">
                            <b-form @submit="onSubmit">
                                <b-form-group id="xray-file-group"
                                              label="X-ray PNG image:"
                                              label-for="xray-file">
                                    <b-form-file
                                            id="xray-file"
                                            @change="onXrayUpload"
                                            v-model="inputXrayFile"
                                            accept="image/png"
                                            required
                                            :state="Boolean(inputXrayFile)"
                                            placeholder="Choose a file or drop it here..."
                                            drop-placeholder="Drop file here...">
                                    </b-form-file>
                                </b-form-group>

                                <b-form-group id="mask-file-group"
                                              label="Mask PNG image:"
                                              label-for="mask-file">
                                    <b-form-file
                                            id="mask-file"
                                            @change="onMaskUpload"
                                            v-model="inputMaskFile"
                                            accept="image/png"
                                            required
                                            :state="Boolean(inputMaskFile)"
                                            placeholder="Choose a file or drop it here..."
                                            drop-placeholder="Drop file here...">
                                    </b-form-file>
                                </b-form-group>
                                <b-button v-if="inputXrayFile && inputMaskFile && !error"
                                          type="submit"
                                          variant="primary">
                                    Submit
                                </b-button>
                            </b-form>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12 d-flexjustify-content-between">
                            <b-img class="mr-1 mt-3 mb-1" v-if="inputXrayUrl" :src="inputXrayUrl"
                                   fluid alt="X-ray file">
                            </b-img>
                            <b-img class="ml-1 mt-3 mb-1" v-if="inputMaskUrl" :src="inputMaskUrl"
                                   fluid alt="Mask file">
                            </b-img>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-6">
                <div class="container-fluid">
                    <div class="row">
                        <div class="col-12">
                            <h3 v-if="prFileUrl">Result</h3>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-12">
                            <b-img class="mr-1 mt-3 mb-1" v-if="prFileUrl" :src="prFileUrl"
                                   fluid alt="Processed mask">
                            </b-img>
                            <b-img class="ml-1 mt-3 mb-1" v-if="resFileUrl" :src="resFileUrl"
                                   fluid alt="Layered">
                            </b-img>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style>
    .loading-overlay {
        opacity:    0.5;
        background: #000;
        width:      100%;
        height:     100%;
        z-index:    10;
        top:        0;
        left:       0;
        position:   fixed;
    }
</style>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      inputXrayFile: null,
      inputXrayUrl: null,
      inputMaskFile: null,
      inputMaskUrl: null,
      resFileUrl: null,
      prFileUrl: null,
      showLoading: false,
      errorMessage: null,
      error: false,
    };
  },
  methods: {
    onSubmit(evt) {
      evt.preventDefault();
      this.showLoading = true;
      const formData = new FormData();
      formData.append('xray', this.inputXrayFile);
      formData.append('mask', this.inputMaskFile);
      axios.post(
        `http://${process.env.VUE_APP_HOST}:5000/upload-image`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          responseType: 'text',
        },
      ).then((res) => {
        this.showLoading = false;
        this.prFileUrl = `http://${process.env.VUE_APP_HOST}:5000/pr?id=${res.data}`;
        this.resFileUrl = `http://${process.env.VUE_APP_HOST}:5000/res?id=${res.data}`;
      }).catch((error) => {
        this.showLoading = false;
        this.error = true;
        this.errorMessage = error.response.data;
      });
    },
    onXrayUpload(e) {
      const file = e.target.files[0];
      this.inputXrayUrl = URL.createObjectURL(file);
      this.error = false;
    },
    onMaskUpload(e) {
      const file = e.target.files[0];
      this.inputMaskUrl = URL.createObjectURL(file);
      this.error = false;
    },
  },
};
</script>
