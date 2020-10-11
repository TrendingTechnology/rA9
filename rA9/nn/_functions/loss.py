import jax.numpy as jnp
from rA9.autograd import Function
from rA9.autograd import Variable


class Spikeloss(Function):
    id = "Spikeloss"

    @staticmethod
    def forward(ctx, input, target, time_step):
        assert isinstance(input, Variable)
        assert isinstance(target, Variable)
        target_np = jnp.squeeze(jnp.eye(len(input.data))[target.data.reshape(-1)])

        def np_fn(input_np, target_np,time_step):
            return (1 / 2) * jnp.sum((input_np - target_np) ** 2)

        np_args = (input.data, target_np, time_step)
        return np_fn, np_args, np_fn(*np_args)

    @staticmethod
    def backward(ctx, grad_outputs):
        return super(Spikeloss, Spikeloss).backward(ctx, grad_outputs)